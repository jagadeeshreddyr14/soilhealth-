from regex import E
from logs import MyLogger
import ee
import glob
import pandas as pd
import datetime
import os
import numpy as np
from rasterio.transform import from_origin
from zonalstats import get_zonal_stats
import time
import subprocess
from subprocess import call
from pyproj import Geod
import configparser


from soil_health import generate_points, get_predictor_bands, xcor, genPredictions, getDataFrame, saveTiff
from ndvi_barren import get_end_date, read_farm
from _push_s3 import uploadfile
from _create_png import create_png
from subprocess import call,Popen,PIPE
import atexit

import warnings
warnings.filterwarnings("ignore")


def roundoff(x):
    if x.name in ['P', 'K', 'N']:
        return x.fillna(np.nan).astype(np.int32, errors='ignore')
    elif x.name in ['OC', 'pH']:
        return x.fillna(np.nan).round(decimals=2)
    else:
        return x


def gen_raster_save_tiff(nut, nut_slr, df_pred, df_temp, path_tiff, transform, farmid, leny, lenx, start_date):

    df_cpy = df_pred.copy()
    predictions = genPredictions(nut, nut_slr, df_cpy.values)
    df_cpy['prediction'] = predictions
    df_out = pd.merge(df_temp, df_cpy, left_index=True,
                      right_index=True, how='left')['prediction']
    data_array = df_out.values.reshape(leny, lenx)
    data_array = np.flip(data_array, axis=0)
    saveTiff(nut, path_tiff, data_array, transform, farmid, start_date)

    return None


def format_zonal_stats(zonalstats, farmid, startdate, path_csv='../output/csv/', save_as_csv=False):

    zonalstats_tmp = zonalstats.copy()
    zonalstats_tmp['date'] = startdate
    dfl = pd.DataFrame(zonalstats_tmp)
    dfl.rename(index={'median': 'average', 'percentile_5': 'min',
                      'percentile_95': 'max'}, inplace=True)

    dfl = dfl.apply(lambda x: roundoff(x))
    # dfl.pH = dfl.pH.apply(lambda x: x-1 if (x > 7) else x)
    os.makedirs(os.path.dirname(path_csv), exist_ok=True)
    if save_as_csv:
        dfl.to_csv(f"{path_csv}/{farmid}.csv")
    logger.info(f'save output csv {farmid}')

    return None


def save_empty_csv(path_csv):

    dfl = pd.DataFrame(columns=['K', 'N', 'P', 'OC', 'pH', 'date'], index=[
                       'average', 'min', 'max'])

    dfl.to_csv(path_csv)


def compute_soil_health(farm_path, pixel_size, pred_bands, soil_nutrients, nuts_ranges, path_tiff, path_png=None,
                        path_csv=None, client_info=None, report = False):

    global logger
    logger = MyLogger(module_name=__name__,
                      filename="../logs/soil_health.log").create_logs()
    '''
    main function we pass input farm in csv(polygon values)
    '''

    farm_id = os.path.basename(farm_path).split(".")[0]

    save_path_tiff = os.path.join(path_tiff, f"{farm_id}")

    if path_csv:
        save_csv_stats = os.path.join(path_csv, f"{farm_id}.csv")
        process_csv = True
    else:
        process_csv = False

    if path_png:
        save_path_png = os.path.join(path_png, f"{farm_id}")
        process_png = True
    else:
        process_png = False

    if os.path.exists(save_csv_stats):
        print('file exists')
        # return

    # checking crop type and client id 
    if client_info:
        client_data = pd.read_csv(client_info)
        # try:
        # not_crop = ['Agarwood', 'Coconut', 'Mango', 'Avocado', ]
        #     farm_crop = list(client_data.loc[(client_data['farm_id'] ==
        #                                       int(farm_id))]['croptype'])[0]

        # except:
        #     farm_crop = ''
        #     pass

        # if farm_crop in not_crop:
        #     return
        
        try:
            id_client = client_data.loc[(client_data['farm_id']==int(farm_id)),['client_id']].values[0]
            # id_client 
        except:
            pass

    try:
        if get_area(farm_path) < 150:

            return logger.warning(f"Farm size small saving empty csv: {farm_path}")
    except Exception as e:
        logger.error(f"farm file format is wrong: {farm_id}")
        return
    #logger.info(f"process starting for = {farm_id}")
    x_pt, y_pt, minx, maxy = generate_points(farm_path, pixel_size)
    len_y, len_x = len(y_pt.getInfo()), len(x_pt.getInfo())
    geometry = ee.FeatureCollection(x_pt.map(xcor(y_pt))).flatten()
    end_date = get_end_date(farm_path)

    try:
        start_date = end_date - datetime.timedelta(days=30)
    except Exception as TypeError:
        logger.error(f"{TypeError}")
        return
    predictor_bands = get_predictor_bands(geometry, start_date, end_date)
    try:
        df = getDataFrame(predictor_bands, pred_bands, geometry)
    except Exception as TypeError:
        logger.error(f"{TypeError}")
        return

    df_tmp = df[["longitude", "latitude"]]
    df_pred = df.loc[df['NDWI'].notna(), pred_bands]
    transform = from_origin(minx, maxy, pixel_size, pixel_size)

    '''Generating raster(tiff)'''
    for nut, nut_slr in soil_nutrients:

        try:
            gen_raster_save_tiff(nut, nut_slr, df_pred, df_tmp, save_path_tiff, transform,
                                 farm_id, len_y, len_x, start_date)

        except Exception as e:
            print(e)
            if process_csv:
                save_empty_csv(save_csv_stats)
            logger.error(f"{e} ")
            return
    logger.info(f"Raster generated for {farm_id}")
    
    '''Generating PNG'''
    if process_png:

        create_png(farm_path, farm_id, save_path_tiff,
                   nuts_ranges, save_path_png)
        logger.info(f'png generated for {farm_id}')
        
    '''Generating CSV(NPK)'''
    if process_csv:
        zonal_stats = get_zonal_stats(farm_path, save_path_tiff)
        format_zonal_stats(zonal_stats, farm_id, start_date,
                           path_csv, save_as_csv=True)
    logger.info(f"process complete for {farm_id}!")

    '''Generating report'''
    
    if report == True:
    
        proc = Popen(["R --vanilla --args < /home/satyukt/Projects/1000/soil_health/src/new_script.r %s" %(farm_id)], shell=True,stdout=PIPE)
        proc.communicate()
        atexit.register(proc.terminate)
        pid = proc.pid
        
        #push s3 
        # id_client = '1936'
        
        local_path = f'/home/satyukt/Projects/1000/soil_health/output/Report/{farm_id}.pdf'

        s3path = f'sat2farm/{id_client}/{farm_id}/soilReportPDF/{farm_id}.pdf'
        
        #pushed to s3
        uploadfile(local_path,s3path)
        print('pushed to s3')
        
        files = glob.glob('*.log')
        for logs in files:
            os.remove(logs) 
    
    

    return None

def get_path(param, fdr_name):
    nnut = glob.glob(f"{model_path + fdr_name[0]}/{param}*.pkl")[0]
    nslr = glob.glob(f"{model_path + fdr_name[1]}/{param}*.pkl")[0]
    return nnut, nslr


def get_area(farm_path):

    farm_poly = read_farm(farm_path).values[0]
    # specify a named ellipsoid: geodesic area
    geod = Geod(ellps="WGS84")
    area = abs(geod.geometry_area_perimeter(farm_poly)[0])

    return area


if __name__ == "__main__":

    start = time.time()

    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)

    ee.Initialize()

    config = configparser.ConfigParser()
    config.read('../Config/config.ini')

    area_path = config['Default']['area_path']
    model_path = config['Default']['model_path']

    path_tiff = config['Output_path']['path_tiff']
    path_csv = config['Output_path']['path_csv']
    path_png = config['Output_path']['path_png']

    client_info = config['aws']['client_info']
    # client_info = None
    if not os.path.exists(path_tiff):
        os.makedirs(path_tiff)

    if not os.path.exists(path_csv):
        os.makedirs(path_csv)

    if not os.path.exists(path_png):
        os.makedirs(path_png)

    nuts_ranges = {
        'N': (100, 300),
        'P': (5, 50),
        'K': (100, 250),
        'pH': (6, 8.5),
        'OC': (0.3, 0.75)
    }

    pixel_size = 0.000277777778/3  # 30 meter by 3 -> 10 meter
    input_bands = ['B8', 'B4', 'B5', 'B11', 'B9', 'B1',
                   'SR_n2', 'SR_N', 'TBVI1', 'NDWI', 'NDVI_G']

    soil_nuts = [get_path(param, ["ml", "slr"])
                 for param in ['pH', 'P', 'K', 'OC', 'N']]
    

    # area_path = "/home/satyukt/Desktop/Manish/wkt_to_shp/create_wkt/area/"
    farm_list = glob.glob(os.path.join(area_path, "*.csv"))
    for i, farm_path in enumerate(farm_list):

        farm_path = "/home/satyukt/Projects/1000/area/30807.csv"
        # farm_path = "/home/satyukt/Projects/1000/sat2credit/area/2405.csv"
        try:
            compute_soil_health(farm_path, pixel_size, input_bands,
                                soil_nuts, nuts_ranges, path_tiff, path_png, path_csv, client_info,report =True)
        except Exception as e:
            print(e)
        
        end = time.time()
        print(end-start)
        exit()

    # subprocess.call(["sh", "rsync_aws.sh"])
