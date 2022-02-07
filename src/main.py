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

from soil_health import generate_points, get_predictor_bands, xcor, genPredictions, getDataFrame, saveTiff, read_farm
from ndvi_barren import get_end_date

from subprocess import call
from pyproj import Geod

import warnings
warnings.filterwarnings("ignore")


def roundoff(x):
    if x.name in ['P', 'K', 'N']:
        return x.fillna(np.nan).astype(np.int32, errors='ignore')
    elif x.name in ['OC', 'pH']:
        return x.fillna(np.nan).round(decimals=2)
    else:
        return x


def gen_raster_save_tiff(nut, nut_slr, df_pred, df_temp, path_tiff, transform, farmid, leny, lenx):

    df_cpy = df_pred.copy()
    predictions = genPredictions(nut, nut_slr, df_cpy.values)
    df_cpy['prediction'] = predictions
    df_out = pd.merge(df_temp, df_cpy, left_index=True,
                      right_index=True, how='left')['prediction']
    data_array = df_out.values.reshape(leny, lenx)
    data_array = np.flip(data_array, axis=0)
    saveTiff(nut, path_tiff, data_array, transform, farmid)

    return None


def format_zonal_stats(zonalstats, farmid, startdate, path_csv='../output/csv/', save_as_csv=False):

    zonalstats_tmp = zonalstats.copy()
    zonalstats_tmp['date'] = startdate
    dfl = pd.DataFrame(zonalstats_tmp)
    dfl.rename(index={'median': 'average', 'percentile_5': 'min',
                      'percentile_95': 'max'}, inplace=True)

    dfl = dfl.apply(lambda x: roundoff(x))

    if save_as_csv:
        dfl.to_csv(f"{path_csv}/{farmid}.csv")

    return None


def main(farm_path, pixel_size, pred_bands, soil_nutrients, path_tiff, path_csv):

    farm_id = os.path.basename(farm_path).split(".")[0]
    save_csv_stats = os.path.join(path_csv, f"{farm_id}.csv")

    if os.path.exists(save_csv_stats):
        logger.info(f"Farm CSV exists: {save_csv_stats}")
        return None

    if get_area(farm_path) < 150:
        return logger.error(f"Farm size small: {farm_path}")

    x_pt, y_pt, minx, maxy = generate_points(farm_path, pixel_size)
    len_y, len_x = len(y_pt.getInfo()), len(x_pt.getInfo())
    geometry = ee.FeatureCollection(x_pt.map(xcor(y_pt))).flatten()

    end_date = get_end_date(farm_id)
    start_date = end_date - datetime.timedelta(days=30)

    predictor_bands = get_predictor_bands(geometry, start_date, end_date)
    df = getDataFrame(predictor_bands, pred_bands, geometry)
    df_tmp = df[["longitude", "latitude"]]
    df_pred = df.loc[df['NDWI'].notna(), pred_bands]

    transform = from_origin(minx, maxy, pixel_size, pixel_size)

    for nut, nut_slr in soil_nutrients:
        
        try:
            gen_raster_save_tiff(nut, nut_slr, df_pred, df_tmp, path_tiff, transform,
                                 farm_id, len_y, len_x)
        except ValueError as e:
            logger.error(f"{e}")
            return

    zonal_stats = get_zonal_stats(farm_path, f"{path_tiff}/{farm_id}")

    format_zonal_stats(zonal_stats, farm_id, start_date,
                       path_csv, save_as_csv=True)
    logger.info(f"process complete for {farm_id}!")
    # call(["rsync", "-avh", "--ignore-existing", "-e", "ssh", "/home/satyukt/Projects/1000/micro_v2/stat1/", "/data1/satyukt/Projects/1000/aws/stats"])

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

    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)

    logger = MyLogger(module_name=__name__, filename="../logs/soil_health.log")

    start = time.time()
    ee.Initialize()

    model_path = '../data/models/'
    save_path_tiff = '../output/tif'
    save_path_csv = '../output/csv/'

    pixel_size = 0.000277777778/3  # 30 meter by 3 -> 10 meter
    input_bands = ['B8', 'B4', 'B5', 'B11', 'B9', 'B1',
                   'SR_n2', 'SR_N', 'TBVI1', 'NDWI', 'NDVI_G']

    soil_nuts = [get_path(param, ["ml", "slr"])
                 for param in ['pH', 'P', 'K', 'OC', 'N']]
    
    default_path = '/data1/BKUP/micro_v2/s1_rvi/area/'
    farm_list = glob.glob(os.path.join(default_path, "[0-9]*.csv"))

    for i, farm_path in enumerate(farm_list):
        
        if i> 20:
            break
        main(farm_path, pixel_size, input_bands,
                        soil_nuts, save_path_tiff, save_path_csv)

    end = time.time()

    print(end-start)
