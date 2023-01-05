from importlib.resources import path
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
from pyproj import Geod
import configparser
from subprocess import Popen,PIPE
import atexit
import ast
from shapely.geometry import shape
import subprocess

from soil_health import generate_points, get_predictor_bands, xcor, genPredictions, getDataFrame, saveTiff
from ndvi_barren import get_end_date, read_farm
from _push_s3 import uploadfile
from _create_png import create_png
from _fetch_gcp import gcp_check
from _get_detials import get_info

import warnings
warnings.filterwarnings("ignore")



def roundoff(x):
    if x.name in ['P', 'K', 'N']:
        return x.fillna(np.nan).astype(np.int32, errors='ignore')
    elif x.name in ['OC', 'pH']:
        return x.fillna(np.nan).round(decimals=2)
    else:
        return x


def gen_raster_save_tiff(nut, nut_slr, df_pred, df_temp, transform, farmid, leny, lenx):

    df_cpy = df_pred.copy()
    predictions = genPredictions(nut, nut_slr, df_cpy.values)
    df_cpy['prediction'] = predictions
    df_out = pd.merge(df_temp, df_cpy, left_index=True,
                      right_index=True, how='left')['prediction']
    data_array = df_out.values.reshape(leny, lenx)
    data_array = np.flip(data_array, axis=0)
    saveTiff(nut, data_array, transform, farmid)

    return None


def format_zonal_stats(zonalstats, farmid, startdate):

    zonalstats_tmp = zonalstats.copy()
    zonalstats_tmp['date'] = startdate
    dfl = pd.DataFrame(zonalstats_tmp)
    dfl.rename(index={'median': 'average', 'percentile_5': 'min',
                      'percentile_95': 'max'}, inplace=True)

    dfl = dfl.apply(lambda x: roundoff(x))
    
    
    path_csv = f"../output/csv/{farmid}.csv"
    
    os.makedirs(os.path.dirname(path_csv), exist_ok=True)
    dfl.to_csv(path_csv)

    return None

def get_area(farm_path):

    
    farm_poly = read_farm(farm_path).values[0]
    # specify a named ellipsoid: geodesic area
    geod = Geod(ellps="WGS84")
    area = abs(geod.geometry_area_perimeter(farm_poly)[0])

    return area

def get_path(param, fdr_name):
    nnut = glob.glob(f"{model_path + fdr_name[0]}/{param}*.pkl")[0]
    nslr = glob.glob(f"{model_path + fdr_name[1]}/{param}*.pkl")[0]
    return nnut, nslr

def compute_soil_health(farm_cor, pixel_size, pred_bands, soil_nutrients, nuts_ranges, lang, report = False, push_s3 = False):
    

    global logger
    logger = MyLogger(module_name=__name__,
                      filename="../logs/soil_health.log").create_logs()
    
    '''
    main function we pass input farm in csv(polygon values)
    '''

    if isinstance(farm_cor, str):
        farm_id = os.path.basename(farm_cor).split('.')[0]
        con = False
    else:
        con = True
        farm_id = str(farm_cor)
        
    fid_ti = f"{farm_id}_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}"

    report_path = f'../output/Report/{farm_id}.pdf'
    
    if os.path.exists(report_path):
        logger.info(f'{farm_id} - report exists')
        return 

    ''' getting farm detail'''        
    try:
        df, referal_code = get_info(int(farm_id))
        id_client, poly, crop = df

        if con == True:
                poly = poly.replace("'", '"')
                cords = ast.literal_eval(poly)
                farm_path = shape(cords["geo_json"]["geometry"])
    except Exception as e:
        logger.error(f'{farm_id} = {e} ')
        return 
        
        
    if get_area(farm_path) < 150:
        local_path = f'../data/Report_data/nodata/Farmsmall.pdf'
        s3path = f'sat2farm/{id_client}/{farm_id}/soilReportPDF/{fid_ti}.pdf'
        uploadfile(local_path,s3path)  
        return logger.warning(f"Farm size small {farm_id}")

    
    logger.info(f'Process started for {farm_id}')
    x_pt, y_pt, minx, maxy = generate_points(farm_path, pixel_size)
    len_y, len_x = len(y_pt.getInfo()), len(x_pt.getInfo())
    geometry = ee.FeatureCollection(x_pt.map(xcor(y_pt))).flatten()
    end_date_lis = get_end_date(farm_path)
    
    for ind,end_date in reversed(list(enumerate(end_date_lis))):
        start_date = end_date - datetime.timedelta(days=30)
        mid_date = end_date - datetime.timedelta(days=15)
        predictor_bands = get_predictor_bands(geometry, start_date, end_date)
        try:
            df = getDataFrame(predictor_bands, pred_bands, geometry)
            df_na = df.dropna()
            if not df_na.empty:
                break
        except:
            continue
    else: 
        local_path = f'../data/Report_data/nodata/Nodata.pdf'
        s3path = f'sat2farm/{id_client}/{farm_id}/soilReportPDF/{fid_ti}.pdf'
        uploadfile(local_path,s3path)
        logger.info( 'No bands available')
        
        return 
        
    df_tmp = df[["longitude", "latitude"]]
    df_pred = df.loc[df['NDWI'].notna(), pred_bands]
    transform = from_origin(minx, maxy, pixel_size, pixel_size)

    '''Generating raster(tiff)'''
    for nut, nut_slr in soil_nutrients:


        gen_raster_save_tiff(nut, nut_slr, df_pred, df_tmp, transform,
                                farm_id, len_y, len_x)

    '''Generating CSV(NPK)'''
    zonal_stats = get_zonal_stats(farm_path, farm_id)
    
    format_zonal_stats(zonal_stats, farm_id, mid_date)
    
    """Generating PNG"""

    create_png(farm_path, farm_id, mid_date,
                nuts_ranges)
          
    '''lat and long for reverse geocode'''
        
    lat = read_farm(farm_path).centroid[0].y
    long = read_farm(farm_path).centroid[0].x
       
    if report == True :
        
        if crop == None:
            crop = ''
            
        if referal_code == None:
            referal_code = ''
        
        subprocess.call(['Rscript', 'GenerateReport.R', str(farm_id), str(crop), str(referal_code), str(lat), str(long), lang])


    if push_s3 == True:  
        
        
        s3path = f'sat2farm/{id_client}/{farm_id}/soilReportPDF/{fid_ti}.pdf'
        
        '''Push to S3'''
        uploadfile(report_path, s3path)
        logger.info(f'pushed to aws {id_client} = {farm_id}')
        
    
    return None


    
    
    
    
    
    
    
    
    
    
        
    
    
    
    
    
    
        
    
    
        
    
    

   
        
    
    
        
    
        
    
        
        
        
    
        
         
     
    

