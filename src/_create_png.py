import rasterio as rio
import matplotlib.pyplot as plt
import glob
import os
from matplotlib import colors
import shapely
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt



def create_png(farm_cor, farm_id, plt_date, nuts_ranges):
    
    tif_loc = f'../output/tif/{farm_id}'
    
    
    tif_files = glob.glob(f"{tif_loc}/*")

    if isinstance(farm_cor, str):
        file = open(farm_cor, "r")
        footprint = file.read()
        file.close
    else:
        footprint = farm_cor.wkt

    shapely_poly = shapely.wkt.loads(footprint)
    crs = {'init': 'epsg:4326'}
    polygon = gpd.GeoDataFrame(
        index=[0], crs=crs, geometry=[shapely_poly])
    extent_gdf = polygon.bounds.values[0]
    buff = 0.00008
    x_axis = [extent_gdf[0]-buff, extent_gdf[2]+buff]
    y_axis = [extent_gdf[1]-buff, extent_gdf[3]+buff]

    # generating MBR for farm polygon
    poly_bound = Polygon([[extent_gdf[0], extent_gdf[1]],
                          [extent_gdf[2], extent_gdf[1]],
                          [extent_gdf[2], extent_gdf[3]],
                          [extent_gdf[0], extent_gdf[3]]])
    crs = {'init': 'epsg:4326'}

    polygon_bound = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[poly_bound])

    clrs = [(0, "#D7191C"), (0.25, "#FDAE61"), (0.5, "#FFFF00"),
            (0.75, "#00FF00"), (1, "#009CFF")]
    cmap = colors.LinearSegmentedColormap.from_list('rsm', clrs, N=256)

    for files in tif_files:
        fig, ax = plt.subplots(figsize=(6, 6), facecolor='white')

        nut = os.path.basename(files).split('.tif')[0].split('_')[-1]

        if nut == 'OC':
            png_title = 'Soil Organic Carbon'
        elif nut == 'N':
            png_title = 'Nitrogen'
        elif nut == 'P':
            png_title = 'Phosphorus'
        elif nut == 'K':
            png_title = 'Potassium'
        elif nut == 'pH':
            png_title = 'pH'
        if nut == 'OC' or nut == 'pH':
            nut_values = list(np.linspace(
                nuts_ranges[nut][0], nuts_ranges[nut][1], 5))
            nut_values = [round(x, 2) for x in nut_values]
        else:
            nut_values = list(np.linspace(
                nuts_ranges[nut][0], nuts_ranges[nut][1], 5))
            nut_values = [int(x) for x in nut_values]

        with rio.open(files, 'r') as src:
            image = src.read(1)

        im = ax.imshow(image, cmap=cmap, vmin=nuts_ranges[nut][0], vmax=nuts_ranges[nut][1], extent=[
            extent_gdf[0], extent_gdf[2], extent_gdf[1], extent_gdf[3]])

        gap = (polygon.overlay(gpd.GeoDataFrame(geometry=polygon_bound.geometry.buffer(
            buff)), how='symmetric_difference')).plot(ax=ax, facecolor='white')

        polygon.plot(ax=ax, facecolor='none', edgecolor='black')
        ax.set_xlim(x_axis)
        ax.set_ylim(y_axis)
        fig.colorbar(im, ticks=nut_values, fraction=0.03, location='right')
        fig.suptitle(
            f"{png_title}\n{plt_date.date()}", ha='center', fontsize='20', va='top', fontweight='bold', fontstyle='normal')
        plt.axis('off')
        
        png_save_path = f"../output/png/{farm_id}/{farm_id}_{nut}.png"
        
        os.makedirs(os.path.dirname(png_save_path), exist_ok=True)

        plt.savefig(png_save_path)


if __name__ == "__main__":

    nuts_ranges = {
        'N': (100, 300),
        'P': (5, 50),
        'K': (100, 250),
        'pH': (5.5, 8),
        'OC': (0.3, 0.75)
    }

    farm_path = "/home/satyukt/Projects/1000/area/55691.csv"

    farm_id = os.path.splitext(os.path.basename(farm_path))[0]
    tif_path = f'/home/satyukt/Projects/1000/soil_health/output/tif/{farm_id}'
    png_save_path = f'/home/satyukt/Desktop/myfiles/soil/png/{farm_id}/'
    create_png(farm_path, farm_id, tif_path, nuts_ranges, png_save_path)
