from rasterstats import zonal_stats
import geopandas as gpd
import pandas as pd
import os
from glob import glob
from shapely.geometry import mapping


def get_feature_geometry(farm_path):

    geom = pd.read_csv(farm_path, header=None, sep='\n')
    ppolygon = mapping(gpd.GeoSeries.from_wkt(geom.values[0])[0])
    
    return ppolygon

def get_zonal_stats(farm_path, raster_path):

    feat = get_feature_geometry(farm_path)
    raster_images = glob(f"{raster_path}/*")
    soil_nutrients = {}
    for raster_image in raster_images:

        raster_filename=os.path.splitext(os.path.basename(raster_image))[0] 
        stats = zonal_stats(feat,raster_image,stats='median percentile_5 percentile_95', geojson_out=True, nodata = -999)
        raster_stats = [ i['properties'] for i in stats]
        soil_nutrients[raster_filename] = raster_stats[0]

    return soil_nutrients



if __name__ == "__main__":


    dirname = os.path.dirname(__file__)
    os.chdir(dirname)

    farm_path = '/data1/BKUP/micro_v2/s1_rvi/area/17994.csv'
    farm_id = os.path.basename(farm_path).split(".")[0]
    raster_images = glob(f"../output/tif/{farm_id}/*.tif")
    
    # read the farm
    geom = pd.read_csv(farm_path, header=None, sep='\n')

    # convert to geojson
    feature = gpd.GeoSeries.from_wkt(geom.iloc[:, 0]).set_crs(
        "EPSG:4326")

    soil_nutrients = {}
    for raster_image in raster_images:
        raster_filename=os.path.splitext(os.path.basename(raster_image))[0] 

        
        stats = zonal_stats(feature,raster_image,stats='median percentile_1', geojson_out=True, nodata = -999)

        raster_stats = [ i['properties'] for i in stats]
        soil_nutrients[raster_filename] = raster_stats[0]

    print(soil_nutrients)