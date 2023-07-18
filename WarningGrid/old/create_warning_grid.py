########################################
######## create_warning_grid.py ########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/05/10 ##########
########################################

import csv
import numpy as np
import geopandas as gpd
from shapely import geometry as gm

def create_warning_grid(warning_range , idx_shp , shp_TWD97 , outPath):
    shpdata_TWD97 = gpd.read_file(shp_TWD97 , encoding = 'utf-8')

    warning_range = sorted(warning_range)
    num_rng = len(warning_range)

    num_x = 441
    num_y = 561
    dx = 0.0125
    dy = 0.0125
    lon_start = 118.0
    lon_end = lon_start + (num_x - 1) * dx
    lat_start = 20.0
    lat_end = lat_start + (num_y - 1) * dy
    map_scale = 10000

    lon = np.arange(lon_start * map_scale , (lon_end + dx) * map_scale , dx * map_scale) / map_scale
    lat = np.arange(lat_start * map_scale , (lat_end + dy) * map_scale , dy * map_scale) / map_scale
    Lon , Lat = np.meshgrid(lon , lat)
    Lon = Lon.T
    Lat = Lat.T

    idx_table = np.empty([num_x , num_y])
    idx_table[:] = np.nan

    ########## Covert Grid ##########
    # WGS84-Longlat (EPSG:4326)
    # TWD97-Longlat (EPSG:3824)
    # TWD67-Longlat (EPSG:3821)
    # TWD97-TM2, lon0=121 (EPSG:3826)
    # TWD97-TM2, lon0=119 (EPSG:3825)
    # TWD67-TM2, lon0=121 (EPSG:3828)
    # TWD67-TM2, lon0=119 (EPSG:3827)

    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        gs_shp_TWD97 = gpd.GeoSeries(shpdata_TWD97.geometry[idx_shp] , crs = 'EPSG:3824')
        for cnt_y in np.arange(0 , num_y):
            for cnt_x in np.arange(0 , num_x):
                if gs_shp_TWD97[0].contains(gm.Point((Lon[cnt_x , cnt_y] , Lat[cnt_x , cnt_y]))):
                    idx_table[cnt_x , cnt_y] = 0
                    writer = csv.writer(fo)
                    writer.writerow([int(idx_table[cnt_x , cnt_y]) , 0 , cnt_x + 1 , cnt_y + 1])

        gs_shp_TWD97_TM2 = gs_shp_TWD97.to_crs('EPSG:3826')
        for cnt_rng in np.arange(0 , num_rng):
            gs_shp_TWD97_TM2_rng = gs_shp_TWD97_TM2.geometry.buffer(warning_range[cnt_rng] * 1000)
            gs_shp_TWD97_rng = gs_shp_TWD97_TM2_rng.to_crs('EPSG:3824')
            for cnt_y in np.arange(0 , num_y):
                for cnt_x in np.arange(0 , num_x):
                    if np.isnan(idx_table[cnt_x , cnt_y]) & gs_shp_TWD97_rng[0].contains(gm.Point((Lon[cnt_x , cnt_y] , Lat[cnt_x , cnt_y]))):
                        idx_table[cnt_x , cnt_y] = cnt_rng + 1
                        writer = csv.writer(fo)
                        writer.writerow([int(idx_table[cnt_x , cnt_y]) , warning_range[cnt_rng] , cnt_x + 1 , cnt_y + 1])