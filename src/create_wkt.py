import geopandas as gpd
import os
import math

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

lon, lat = 76.614365 , 15.342534 

Area_arc = 4 

def buff_radius(Area_arc):
    radius = math.sqrt(4046.86 *5 * Area_arc/ math.pi)
    return (radius*0.0001)/11.1

wkts = [f'POINT ({lon} {lat})']

s = gpd.GeoSeries.from_wkt(wkts)


s.buffer(buff_radius(Area_arc)).set_crs("EPSG:4326").to_csv("../output/client_wkt/test_Siddappa.csv", index=False, header=False)