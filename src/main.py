import ee
import glob
import pandas as pd
import datetime
import os
from rasterio.transform import from_origin

from zonalstats import get_zonal_stats

from soil_health import generate_points, get_predictor_bands, xcor, genPredictions, getDataFrame, saveTiff
from ndvi_barren import get_end_date

import warnings
warnings.filterwarnings("ignore")


def roundoff(x):
    if x.name in ['P', 'K', 'N']:
        return x.astype(int)
    elif x.name in ['OC', 'pH']:
        return x.round(decimals=2)
    else:
        return x


def gen_raster_save_tiff(soil_nuts, input, df_tmp, save_path_tiff, transform, farm_id, len_y, len_x):

    for soilnut in soil_nuts:
        for nut, nut_slr in zip(glob.glob(f'../data/models/{soilnut}.pkl'), glob.glob(f'../data/models/{soilnut}*_slr.pkl')):

            predictions = genPredictions(nut, nut_slr, input)
            df_pred['prediction'] = predictions
            df_out = pd.merge(df_tmp, df_pred, left_index=True,
                            right_index=True, how='left')['prediction']
            data_array = df_out.values.reshape(len_y, len_x)
            saveTiff(nut, save_path_tiff, data_array, transform, farm_id)
            # get_png(nut, save_path_pre, data_array, transform, farm_path, farm_id)
    return None
          

def format_zonal_stats(zonal_stats, farm_id, start_date, save_path_csv='../output/csv/', save_as_csv=False):
    zonal_stats['date'] = start_date
    dfl = pd.DataFrame(zonal_stats)
    dfl.rename(index={'median': 'average', 'percentile_5': 'min',
               'percentile_95': 'max'}, inplace=True)

    dfl = dfl.apply(lambda x: roundoff(x))

    if save_as_csv:
        dfl.to_csv(f"{save_path_csv}/{farm_id}.csv")
        # print(f"{farm_id} saved!" )

    return None


if __name__ == "__main__":

    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)

    pixel_size = 0.000277777778/3  # 30 meter by 3 -> 10 meter

    input_bands = ['B8', 'B4', 'B5', 'B11', 'B9', 'B1', 'SR_n2', 'SR_N', 'TBVI1', 'NDWI', 'NDVI_G']
    soil_nuts = ['pH', 'P', 'K', 'OC', 'N']

    default_path = '/data1/BKUP/micro_v2/s1_rvi/area/'
    farm_list = [f"{default_path}/{farm_id}.csv" for farm_id in [19238]]

    for farm_path in farm_list:

        farm_id = os.path.basename(farm_path).split(".")[0]
        save_path_tiff = '../output/tif/'
        save_path_csv = '../output/csv/'
        x_pt, y_pt, minx, maxy = generate_points(farm_path, pixel_size)
        geometry = ee.FeatureCollection(x_pt.map(xcor(y_pt))).flatten()

        end_date = get_end_date(farm_id)
        start_date = end_date - datetime.timedelta(days=30)
        predictor_bands = get_predictor_bands(geometry, start_date, end_date)

        len_y, len_x = len(y_pt.getInfo()), len(x_pt.getInfo())

        df = getDataFrame(predictor_bands, input_bands, geometry)
        df_tmp = df[["longitude", "latitude"]]
        df_pred = df.loc[df['NDWI'].notna(), input_bands]
        input = df_pred.values
        transform = from_origin(minx, maxy, pixel_size, pixel_size)

        _ = gen_raster_save_tiff(soil_nuts, input, df_tmp, save_path_tiff, transform, farm_id, len_y, len_x)
        
        zonal_stats = get_zonal_stats(farm_path, f"{save_path_tiff}/{farm_id}")

        format_zonal_stats(zonal_stats, start_date=start_date, farm_id=farm_id,
                           save_path_csv=save_path_csv, save_as_csv=True)