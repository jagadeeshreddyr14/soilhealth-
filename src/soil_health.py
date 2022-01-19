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
from rasterio.io import MemoryFile
from rio_tiler.io import COGReader
from shapely.geometry import mapping

from indices import NDWI_function,  NDVI_function, NDVI_G_function, SR_n2_function, SR_N_function, TBVI1_function
from ee_utils import addNDVI, clipToCol, maskS2clouds_min_max, maskS2clouds
from zonalstats import get_zonal_stats
import warnings
warnings.filterwarnings("ignore")


# Initialize the library.
ee.Initialize()


def generate_points(farm_path, pixel_size):

    # read the farm
    geom = pd.read_csv(farm_path, header=None, sep='\n')

    # convert to geojson
    feature = gpd.GeoSeries.from_wkt(geom.iloc[:, 0]).set_crs(
        "EPSG:4326").__geo_interface__

    # extract bounds
    minx,	miny, maxx, maxy = feature['bbox']

    x_pt = ee.List.sequence(minx, maxx, pixel_size)
    y_pt = ee.List.sequence(miny, maxy, pixel_size)
    
    return x_pt, y_pt, minx, maxy


# generate points
def xcor(y_pt):
    def wrap(x_each):

        feat = ee.FeatureCollection(y_pt.map(lambda y_each: ee.Feature(
            ee.Geometry.Point([x_each, y_each], ee.Projection("EPSG:4326")))))
        return feat
    return wrap


def masker(greenest, minest):
    def wrap(image):
            
        mask1 = greenest.select('NDVI').gt(0.3)
        mask2 = minest.select('NDVI').lt(0.6)
        mask3 = image.select('NDVI').gt(0.05)
        mask4 = image.select('NDVI').lt(0.3)
        return image.updateMask(mask1).updateMask(mask2).updateMask(mask3).updateMask(mask4)

    return wrap

def get_predictor_bands(geometry, start_date, end_date):
    
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
    minest = s2_NDVI.min()

    predictor_bands = indices_collection.map(masker(greenest, minest))
    
    return predictor_bands

def getDataFrame(predictor_bands, input_bands, geometry):

    df = pd.DataFrame(predictor_bands.select(input_bands).getRegion(geometry.geometry(), 10).getInfo())
    df, df.columns = df[1:], df.iloc[0]
    df = df.drop(["id", "time"], axis=1)

    return df

    
def genPredictions(nut, nut_slr, input):

    with open(nut, 'rb') as file, open(nut_slr, 'rb') as file_slr:

        mymodel, model_scaler = pickle.load(file), pickle.load(file_slr)
        X_test = model_scaler.transform(input)
        predictions = mymodel.predict(X_test)

    return predictions


def get_feature_geometry(farm_path):

    geom = pd.read_csv(farm_path, header=None, sep='\n')
    ppolygon = mapping(gpd.GeoSeries.from_wkt(geom.values[0])[0])
    
    return ppolygon


def get_png(nut ,save_path_pre, data_array, transform, farm_path, farm_id):


    folder_path = "png"
    file_name = os.path.basename(nut).split('.')[0]

    options = {
        "driver": "GTiff",
        "height": data_array.shape[0],
        "width": data_array.shape[1],
        "count": 1,
        "dtype": np.float32,
        "crs": 'EPSG:4326',
        "transform": transform,
    }

    with MemoryFile() as memfile:
        with memfile.open(**options) as dataset:
            
            dataset.write(data_array, 1)
            
        with memfile.open() as src:

            with COGReader(src.name) as cog:
                feat = get_feature_geometry(farm_path)
                img = cog.feature(feat)
                buf = img.render(img_format="png")
                
                if not os.path.exists(f"{save_path_pre}/{folder_path}/{farm_id}"):
                    os.mkdir(os.path.join(f"{save_path_pre}/{folder_path}", str(farm_id) ))
                    
                with open(f"{save_path_pre}/{farm_id}/{farm_id}_{file_name}.png", 'wb') as src:
                    src.write(buf)



def saveTiff(nut, save_path_pre, data_array, transform, farm_id):
    
    folder_path = "tif"
    file_name = os.path.basename(nut).split('.')[0]
    options = {
        "driver": "Gtiff",
        "height": data_array.shape[0],
        "width": data_array.shape[1],
        "count": 1,
        "dtype": np.float32,
        "crs": 'EPSG:4326',
        "transform": transform
    }


    if not os.path.exists(f"{save_path_pre}/{folder_path}/{farm_id}"):
        os.mkdir(os.path.join(f"{save_path_pre}/{folder_path}", str(farm_id) ))

    with rs.open(f"{save_path_pre}/{folder_path}/{farm_id}/{farm_id}_{file_name}.tif", 'w', **options) as src:
        src.write(data_array, 1)


if __name__ == "__main__":
        
    dirname = os.path.dirname(__file__)
    os.chdir(dirname)

    farm_id = 10973
    farm_path = f'/data1/BKUP/micro_v2/s1_rvi/area/{farm_id}.csv'
    save_path_pre = '../output/'
    
    pixel_size = 0.000277777778/3  # 30 meter by 3 -> 10 meter

    start_date = ee.Date(datetime.datetime.now() - datetime.timedelta(days=200) )
    end_date = ee.Date(datetime.datetime.now() - datetime.timedelta(days=150) )

    input_bands = ['B8', 'B4', 'B5', 'B11', 'B9', 'B1', 'SR_n2', 'SR_N', 'TBVI1', 'NDWI', 'NDVI_G']
    soil_nuts = ['pH', 'P', 'K', 'OC', 'N']

    x_pt, y_pt, minx, maxy = generate_points(farm_path, pixel_size)
    geometry = ee.FeatureCollection(x_pt.map(xcor(y_pt))).flatten()
    predictor_bands = get_predictor_bands(geometry, start_date, end_date)

    
    len_y = len(y_pt.getInfo())
    len_x = len(x_pt.getInfo())

    df = getDataFrame(predictor_bands, input_bands, geometry)
    df_tmp = df[["longitude", "latitude"]]
    df_pred = df.loc[df['NDWI'].notna(), input_bands]
    input = df_pred.values
    transform = from_origin(minx, maxy, pixel_size, pixel_size)

    for i in soil_nuts:

        for nut, nut_slr in zip(glob.glob(f'../data/models/{i}.pkl'), glob.glob(f'../data/models/{i}*_slr.pkl')):

            predictions = genPredictions(nut, nut_slr, input)
            
            df_pred['prediction'] = predictions

            df_out = pd.merge(df_tmp, df_pred, left_index=True, right_index=True, how='left')['prediction']

            data_array = df_out.values.reshape( len_y, len_x )
            saveTiff(nut, save_path_pre, data_array, transform, farm_id)
            # get_png(nut, save_path_pre, data_array, transform, farm_path, farm_id)
    
    zonal_stats = get_zonal_stats(farm_path, f"../output/tif/{farm_id}")
    print(zonal_stats)