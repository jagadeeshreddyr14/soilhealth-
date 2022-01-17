import ee

import pickle
import glob
import pandas as pd
import numpy as np
import geopandas as gpd
import datetime
import rasterio as rs
import os
from rasterio.transform import from_origin
from indices import NDWI_function,  NDVI_function, NDVI_G_function, SR_n2_function, SR_N_function, TBVI1_function
from ee_utils import addNDVI, clipToCol, maskS2clouds_min_max, maskS2clouds

import warnings
warnings.filterwarnings("ignore")


# Initialize the library.
ee.Initialize()


# SETTINGS
farm_path = '/data1/BKUP/micro_v2/s1_rvi/area/17613.csv'
pixel_size = 0.000277777778/3  # 30 meter by 3 -> 10 meter

start_date = ee.Date(datetime.datetime.now() - datetime.timedelta(days=30))
end_date = ee.Date(datetime.datetime.now())

input_bands = ['B8', 'B4', 'B5', 'B11', 'B9', 'B1',
               'SR_n2', 'SR_N', 'TBVI1', 'NDWI', 'NDVI_G']

soil_nuts = ['pH', 'P', 'K', 'OC', 'N']

# read the farm
geom = pd.read_csv(farm_path, header=None, sep='\n')

# convert to geojson
feature = gpd.GeoSeries.from_wkt(geom.iloc[:, 0]).set_crs(
    "EPSG:4326").__geo_interface__

# extract bounds
minx,	miny,	maxx, maxy = feature['bbox']


x_pt = ee.List.sequence(minx, maxx, pixel_size)
y_pt = ee.List.sequence(miny, maxy, pixel_size)

len_x = len(x_pt.getInfo())
len_y = len(y_pt.getInfo())


# generate points
def xcor(x_each):

    feat = ee.FeatureCollection(y_pt.map(lambda y_each: ee.Feature(
        ee.Geometry.Point([x_each, y_each], ee.Projection("EPSG:4326")))))
    return feat


geometry = ee.FeatureCollection(x_pt.map(xcor)).flatten()

s2_sr = ee.ImageCollection("COPERNICUS/S2_SR")


s2_sr_filter = s2_sr.filterBounds(geometry.geometry()).filterDate(
    start_date, end_date).map(maskS2clouds)

sentinel2 = ee.ImageCollection(s2_sr_filter.mosaic().set(
    "system:time_start", ee.Image(s2_sr_filter.first()).get("system:time_start")))


indices_collection = sentinel2.map(NDWI_function).map(TBVI1_function).map(
    NDVI_G_function).map(SR_N_function).map(SR_n2_function).map(NDVI_function)


s2_NDVI = ee.ImageCollection('COPERNICUS/S2_SR').filterBounds(geometry).filterDate('2020-01-01', '2020-12-31')\
    .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 50)).map(maskS2clouds_min_max).map(addNDVI).select("NDVI").map(clipToCol(geometry))


greenest = s2_NDVI.qualityMosaic('NDVI')
min = s2_NDVI.min()


def masker(image):
    mask1 = greenest.select('NDVI').gt(0.3)
    mask2 = min.select('NDVI').lt(0.6)
    mask3 = image.select('NDVI').gt(0.05)
    mask4 = image.select('NDVI').lt(0.3)
    return image.updateMask(mask1).updateMask(mask2).updateMask(mask3).updateMask(mask4)


predictor_bands = indices_collection.map(masker)

df = pd.DataFrame(predictor_bands.select(
    input_bands).getRegion(geometry.geometry(), 10).getInfo())
df, df.columns = df[1:], df.iloc[0]
df = df.drop(["id", "time"], axis=1)
df_tmp = df[["longitude", "latitude"]]
df_pred = df.loc[df['NDWI'].notna(), input_bands]

input = df_pred.values



if __name__ == "__main__":
        
    dirname = os.path.dirname(__file__)
    
    os.chdir(dirname)

    output_path = "../output"

    for i in soil_nuts:

        for nut, nut_slr in zip(glob.glob(f'../data/models/{i}.pkl'), glob.glob(f'../data/models/{i}*_slr.pkl')):

            with open(nut, 'rb') as file, open(nut_slr, 'rb') as file_slr:

                mymodel, model_scaler = pickle.load(file), pickle.load(file_slr)
                X_test = model_scaler.transform(input)
                predictions = mymodel.predict(X_test)

                df_pred['prediction'] = predictions

                df_out = pd.merge(df_tmp, df_pred, left_index=True,
                                right_index=True, how='left')['prediction']

                arr = df_out.values.reshape(len_y, len_x)
                transform = from_origin(minx, maxy, 0.000277777778/3, 0.000277777778/3)

                options = {
                    "driver": "Gtiff",
                    "height": arr.shape[0],
                    "width": arr.shape[1],
                    "count": 1,
                    "dtype": np.float32,
                    "crs": 'EPSG:4326',
                    "transform": transform
                }

            with rs.open(f"{output_path}/{os.path.basename(nut).split('.')[0]}.tif", 'w', **options) as src:
                src.write(arr, 1)
