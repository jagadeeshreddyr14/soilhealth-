import ee
import pandas as pd
from ee_utils import addNDVI, maskS2clouds
from shapely.geometry import mapping
import geopandas as gpd
import os
import datetime


def read_farm(farm_path, setcrs=False):

    geom = pd.read_csv(farm_path, header=None, sep='\n')

    farm_poly = gpd.GeoSeries.from_wkt(geom.iloc[:, 0])

    if setcrs:
        return farm_poly.set_crs("EPSG:4326")

    return farm_poly


def get_py_geometry(farm_path):

    farm_poly = read_farm(farm_path)
    ppolygon = mapping(farm_poly[0])

    return ppolygon


def get_ee_Geometry(farm_path):

    farm_poly = read_farm(farm_path)

    pjson = mapping(farm_poly[0])

    ppolygon = ee.Geometry.Polygon(pjson['coordinates'])

    return ee.FeatureCollection(ppolygon)


def timeSeries(geometry, fname):
    def wrap(image):
        stats = image.reduceRegion(**{
            "reducer": ee.Reducer.median(),
            "geometry": geometry.geometry(),
            "scale": 10,
            "maxPixels": 1e13
        })

        sentinelSM = ee.List([stats.get(fname), -9999]
                             ).reduce(ee.Reducer.firstNonNull())

        f = ee.Feature(None, {fname: sentinelSM, 'date': ee.Date(
            image.get('system:time_start')).format('YYYY-MM-dd')})

        return f
    return wrap


def get_end_date(farm_path):

    features = get_ee_Geometry(farm_path)

    start_date = ee.Date(datetime.datetime.now() -
                         datetime.timedelta(days=360))
    current_date = ee.Date(datetime.datetime.now() -
                           datetime.timedelta(days=0))

    imageCollection = ee.ImageCollection("COPERNICUS/S2_SR")\
                        .filterDate(start_date, current_date)\
                        .filterBounds(features.geometry())\
                        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 50))\
                        .map(maskS2clouds).map(addNDVI).select("NDVI")

    smTimeSeries = imageCollection.map(timeSeries(features, fname="NDVI"))

    sm_info = {"SM": {key['properties']['date']: key['properties']['NDVI']
                      for key in smTimeSeries.getInfo()['features']}}

    df_sm = pd.DataFrame(sm_info)
    df_sm = df_sm[df_sm.SM > 0]
    df_sm.index = pd.to_datetime(df_sm.index, format='%Y-%m-%d')
    df_sm = df_sm.groupby(pd.Grouper(freq="M")).mean()['SM']
    try:
        end_date = df_sm[df_sm < 0.4].last_valid_index()
    except Exception as e:
        print('not less than')
        end_date = df_sm[df_sm < 0.5].last_valid_index()

    return end_date


if __name__ == "__main__":

    ee.Initialize()

    dirname = os.path.dirname(os.path.abspath(__file__))

    os.chdir(dirname)

    farm_id = 10973
    # end_date = get_end_date(farm_id)
    # print(end_date)
    farm_path = f'/home/satyukt/Projects/1000/area/{farm_id}.csv'

    features = get_ee_Geometry(farm_path)

    imageCollection = ee.ImageCollection("COPERNICUS/S2_SR").filterDate('2021-06-01', '2021-12-30')\
                        .filterBounds(features.geometry())\
                        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 50))\
                        .map(maskS2clouds).map(addNDVI).select("NDVI")

    smTimeSeries = imageCollection.map(timeSeries(features, fname="NDVI"))

    sm_info = {"SM": {key['properties']['date']: key['properties']['NDVI']
                      for key in smTimeSeries.getInfo()['features']}}

    df = pd.DataFrame(sm_info)
    df = df[df.SM > 0]
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    df = df.groupby(pd.Grouper(freq="M")).mean()[
        'SM']  # .to_csv("nellore_Pet.csv")
    end_date = df[df < 0.4].last_valid_index()
    print(end_date)
