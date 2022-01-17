from rasterstats import zonal_stats
import geopandas as gpd
import pandas as pd
import os
from glob import glob



dirname = os.path.dirname(__file__)
os.chdir(dirname)

raster_images = glob("../output/*.tif")
farm_path = '/data1/BKUP/micro_v2/s1_rvi/area/17613.csv'

# read the farm
geom = pd.read_csv(farm_path, header=None, sep='\n')

# convert to geojson
feature = gpd.GeoSeries.from_wkt(geom.iloc[:, 0]).set_crs(
    "EPSG:4326")

soil_nutrients = {}
for raster_image in raster_images:
    raster_filename=os.path.splitext(os.path.basename(raster_image))[0] 

    
    stats = zonal_stats(feature,raster_image,stats='median', geojson_out=True, nodata = -999)

    raster_stats = [ i['properties'] for i in stats]
    soil_nutrients[raster_filename] = raster_stats[0]['median']

print(soil_nutrients)