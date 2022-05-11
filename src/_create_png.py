import rasterio as rio
import matplotlib.pyplot as plt
import glob
import os
from matplotlib import colors
import shapely
import geopandas as gpd
from shapely.geometry import Polygon
import datetime
import numpy as np


def create_png(farm_path, tif_path, nuts_ranges, png_save_path):

    tif_files = glob.glob(f"{tif_path}/*")

    file = open(farm_path, "r")
    footprint = file.read()
    file.close()

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

        dae = os.path.splitext(os.path.basename(files))[0]
        date_string = dae.split('_')[1]
        nut = dae.split('_')[2]
        plt_date = str(datetime.datetime.strptime(
            date_string, "%Y%m%d").date())

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
            f"{nut}\n{plt_date}", ha='center', fontsize='20', va='top', fontweight='bold', fontstyle='normal')
        plt.axis('off')
        if not os.path.exists(png_save_path):

            os.makedirs(png_save_path)
        plt.savefig(f"{png_save_path}/{nut}_{date_string}.png")


if __name__ == "__main__":

    nuts_ranges = {
        'N': (100, 300),
        'P': (5, 50),
        'K': (100, 250),
        'pH': (6, 8.5),
        'OC': (0.3, 0.75)
    }

    farm_path = "/home/satyukt/Projects/1000/area/1153.csv"
    farm_id = os.path.splitext(os.path.basename(farm_path))[0]
    tif_path = f'/home/satyukt/Projects/1000/soil_health/output/tif/{farm_id}'
    png_save_path = f'/home/satyukt/Projects/1000/soil_health/output/png/{farm_id}/'
    create_png(farm_path, tif_path, nuts_ranges, png_save_path)
