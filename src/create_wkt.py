import geopandas as gpd
import os

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

lon, lat = 76.614365 , 15.342534
 
wkts = [f'POINT ({lon} {lat})']

s = gpd.GeoSeries.from_wkt(wkts)

s.buffer(0.0007).set_crs("EPSG:4326").to_csv("../output/client_wkt/test_Nagaraj.csv", index=False, header=False)