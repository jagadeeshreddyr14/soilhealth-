import ee
import pandas as pd
from ee_utils import addNDVI, maskS2clouds
from shapely.geometry import mapping
import geopandas as gpd
import os
import datetime

ee.Initialize()

def getGeometry(farm_path):

    geom = pd.read_csv(farm_path, header=None, sep='\n')

    pjson = mapping(gpd.GeoSeries.from_wkt(geom.values[0])[0])

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
        
        sentinelSM = ee.List([stats.get(fname), -9999]).reduce(ee.Reducer.firstNonNull())
        
        f = ee.Feature(None, {fname: sentinelSM,'date': ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')})
        
        return f
    return wrap


def get_end_date(farm_id):

    farm_path = f'/data1/BKUP/micro_v2/s1_rvi/area/{farm_id}.csv'

    features = getGeometry(farm_path)

    start_date = ee.Date(datetime.datetime.now() - datetime.timedelta(days=360) )
    current_date = ee.Date(datetime.datetime.now() - datetime.timedelta(days=0) )

    imageCollection = ee.ImageCollection("COPERNICUS/S2_SR")\
                        .filterDate(start_date, current_date)\
                        .filterBounds(features.geometry())\
                        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 50))\
                        .map(maskS2clouds).map(addNDVI).select("NDVI")

    smTimeSeries = imageCollection.map(timeSeries(features, fname = "NDVI"))

    sm_info = {"SM": {key['properties']['date']:key['properties']['NDVI'] for key in smTimeSeries.getInfo()['features']} }    

    df = pd.DataFrame(sm_info)
    df = df[df.SM > 0]
    df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')
    df = df.groupby(pd.Grouper(freq="M")).mean()['SM']
    end_date = df[df < 0.4].last_valid_index()

    return end_date




if __name__ == "__main__":

    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)

    farm_id = 10973
    # end_date = get_end_date(farm_id)
    # print(end_date)
    farm_path = f'/data1/BKUP/micro_v2/s1_rvi/area/{farm_id}.csv'

    features = getGeometry(farm_path)

    imageCollection = ee.ImageCollection("COPERNICUS/S2_SR").filterDate('2021-06-01', '2021-12-30')\
                        .filterBounds(features.geometry())\
                        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 50))\
                        .map(maskS2clouds).map(addNDVI).select("NDVI")


    smTimeSeries = imageCollection.map(timeSeries(features, fname = "NDVI"))

    sm_info = {"SM": {key['properties']['date']:key['properties']['NDVI'] for key in smTimeSeries.getInfo()['features']} }    

    df = pd.DataFrame(sm_info)
    df = df[df.SM > 0]
    df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')
    df = df.groupby(pd.Grouper(freq="M")).mean()['SM']#.to_csv("nellore_Pet.csv")
    end_date = df[df < 0.4].last_valid_index()
    print(end_date)

