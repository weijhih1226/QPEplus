########################################
########### write_geojson.py ###########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/07/07 ##########
########################################

########## Grid Information ##########
# WGS84-Longlat (EPSG:4326)
# TWD97-Longlat (EPSG:3824)
# TWD67-Longlat (EPSG:3821)
# TWD97-TM2, lon0=121 (EPSG:3826)
# TWD97-TM2, lon0=119 (EPSG:3825)
# TWD67-TM2, lon0=121 (EPSG:3828)
# TWD67-TM2, lon0=119 (EPSG:3827)

import numpy as np
import geopandas as gpd
import convert_coordinate as cc
from shapely.geometry import Polygon

homeDir = r'C:\Users\wjchen\Documents\Tools\geojson'
outPath = rf'{homeDir}\QPESUMS_Mosaic_grid_921_881.geojson'

res = 0.0125
mtpfct = 100000
lon_start = 115
# lon_end = 116
lon_end = 126.5
lat_start = 18
# lat_end = 19
lat_end = 29
lon = np.arange(lon_start * mtpfct , (lon_end + res) * mtpfct , res * mtpfct) / mtpfct
lat = np.arange(lat_start * mtpfct , (lat_end + res) * mtpfct , res * mtpfct) / mtpfct
lonG = np.arange((lon_start * mtpfct - res * 0.5 * mtpfct) , (lon_end * mtpfct + res * 1.5 * mtpfct) , res * mtpfct) / mtpfct
latG = np.arange((lat_start * mtpfct - res * 0.5 * mtpfct) , (lat_end * mtpfct + res * 1.5 * mtpfct) , res * mtpfct) / mtpfct

gs = []
Lon = []
Lat = []
for cnt_lat in range(len(latG) - 1):
    for cnt_lon in range(len(lonG) - 1):
        gs.append(Polygon([(lonG[cnt_lon] , latG[cnt_lat]) , (lonG[cnt_lon + 1] , latG[cnt_lat]) , (lonG[cnt_lon + 1] , latG[cnt_lat + 1]) , (lonG[cnt_lon] , latG[cnt_lat + 1]) , (lonG[cnt_lon] , latG[cnt_lat])]))
        Lon.append(lon[cnt_lon])
        Lat.append(lat[cnt_lat])
gs = gpd.GeoSeries(gs , crs = 3821).to_crs(3828)

gs_new = []
for cnt_gs in range(len(gs)):
    x67 , y67 = np.array(gs[cnt_gs].exterior.coords.xy)
    x97 , y97 = cc.TWD67toTWD97(x67 , y67)
    gs_new.append(Polygon(zip(x97 , y97)))
gs_new = gpd.GeoSeries(gs_new , crs = 3826).to_crs(3824)

# gdf = gpd.GeoDataFrame({'LongitudeTWD67' : Lon , 'LatitudeTWD67' : Lat , 'geometry' : gs_new}).to_file(outPath , driver = "GeoJSON")