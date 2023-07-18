########################################
########### Read_Mosaic2D.py ###########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/04/28 ##########
########################################

import gzip
import csv
import os
import ctypes as c
import numpy as np
import geopandas as gpd
import cartopy.crs as ccrs
import pyproj
from pyproj import CRS , Proj , Transformer
from shapely import geometry as gm
from matplotlib import pyplot as plt
from sklearn.exceptions import DataDimensionalityWarning
from matplotlib.colors import ListedColormap , BoundaryNorm

def readMosaic2D(filePath):
    if filePath[-3:] == '.gz':
        file = gzip.GzipFile(mode = 'rb' , fileobj = open(filePath , 'rb'))
    else:
        file = open(filePath , 'rb')

    with file as f:
        bytedata = f.read()
        num_byte = len(bytedata)
        param = np.zeros(20 , dtype = np.int64)
        for cnt_byte_grp in np.arange(0 , 20):
            cnt_byte = cnt_byte_grp * 4
            param[cnt_byte_grp] = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')
            param_name = chr(bytedata[3 + cnt_byte]) + chr(bytedata[2 + cnt_byte])
            if cnt_byte_grp == 9:
                if param_name == '  ': iproj = 0
                if param_name == 'PS': iproj = 1
                if param_name == 'LA': iproj = 2
                if param_name == 'ME': iproj = 3
                if param_name == 'LL': iproj = 4
                param[cnt_byte_grp] = iproj
        
        # print(param)
        iyy = param[0]
        im = param[1]
        id = param[2]
        ih = param[3]
        imin = param[4]
        isec = param[5]
        num_x = param[6]
        num_y = param[7]
        num_z = param[8]
        map_scale = param[10]
        alon = param[14] / map_scale
        alat = param[15] / map_scale
        xy_scale = param[16]
        dxy_scale = param[19]
        dx = param[17] / dxy_scale
        dy = param[18] / dxy_scale

        zht = np.zeros(num_z , dtype = int)
        for cnt_byte_grp in np.arange(20 , 20 + num_z):
            cnt_byte = cnt_byte_grp * 4
            zht[cnt_byte_grp - 20] = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')

        for cnt_byte_grp in np.arange(20 + num_z , 21 + num_z):
            cnt_byte = cnt_byte_grp * 4
            z_scale = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')

        for cnt_byte_grp in np.arange(21 + num_z , 22 + num_z):
            cnt_byte = cnt_byte_grp * 4
            i_bb_mode = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')

        cnt_byte_grp = 31 + num_z
        num_byte = cnt_byte_grp * 4

        varName = ''
        varUnit = ''
        for cnt_byte in np.arange(num_byte , num_byte + 20):
            varName += chr(bytedata[cnt_byte])
        varName = varName.strip('\x00')
        for cnt_byte in np.arange(num_byte + 20 , num_byte + 26):
            varUnit += chr(bytedata[cnt_byte])
        varUnit = varUnit.strip('\x00')
        
        cnt_byte = num_byte + 26
        var_scale = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')
        imissing = int.from_bytes(bytedata[cnt_byte + 4 : cnt_byte + 8] , byteorder = 'little')
        nradars = int.from_bytes(bytedata[cnt_byte + 8 : cnt_byte + 12] , byteorder = 'little')

        cnt_byte = cnt_byte + 12
        mosradar = []
        if nradars != 0:
            for cnt_rad in np.arange(0 , nradars):
                cnt_rad_byte = cnt_byte + cnt_rad * 4
                mosradar.append(chr(bytedata[cnt_rad_byte]) + chr(bytedata[cnt_rad_byte + 1]) + chr(bytedata[cnt_rad_byte + 2]) + chr(bytedata[cnt_rad_byte + 3]))
            idx_byte = cnt_rad_byte + 3
        else:
            idx_byte = cnt_byte

        data = np.empty([num_x , num_y])
        for cnt_z in np.arange(0 , num_z):
            for cnt_y in np.arange(0 , num_y):
                for cnt_x in np.arange(0 , num_x):
                    data[cnt_x , cnt_y] = int.from_bytes(bytedata[idx_byte + 1 : idx_byte + 3] , byteorder = 'little') / var_scale
                    if data[cnt_x , cnt_y] < -90:
                        data[cnt_x , cnt_y] = -999
                    if data[cnt_x , cnt_y] == 16383:
                        data[cnt_x , cnt_y] = -999
                    idx_byte += 2

    data[data == -999] = np.nan
    return data

product = 'qpfqpe_060min'
homeDir = r'C:\Users\wjchen\Documents'
inDir = rf'{homeDir}\QPESUMS\grid\{product}'
datetime = '20220510.2330'
inFile = f'qpfqpe_060min.{datetime}.gz'
datatype = 'QPF_1H'
inPath = f'{inDir}\{inFile}'
data = readMosaic2D(inPath)

shp_KHH = r'.\shp\taiwan_county\COUNTY_MOI_1090820.shp'
shp_KHH_warn = r'\\61.56.11.35\qpeplus\001.Qplus客製化\005.縣市\高雄市\易淹水預警區位V4\易淹水預警區位V4.shp'
shpdata_KHH = gpd.read_file(shp_KHH , encoding = 'utf-8')
shpdata_KHH_warn = gpd.read_file(shp_KHH_warn , encoding = 'utf-8')
gs_KHH = gpd.GeoSeries(shpdata_KHH.geometry[15] , crs = "EPSG:3824")
gs_KHH_warn = gpd.GeoSeries(shpdata_KHH_warn.geometry[:] , crs = "EPSG:3828")
gs_KHH = gs_KHH.to_crs("EPSG:3821")
gs_KHH_warn = gs_KHH_warn.to_crs("EPSG:3821")
num_warn = len(gs_KHH_warn)

lon_QPF = np.arange(1180000 , 1235125 , 125) / 10000
lat_QPF = np.arange(200000 , 270125 , 125) / 10000
Lon_QPF , Lat_QPF = np.meshgrid(lon_QPF , lat_QPF)
Lon_QPF = Lon_QPF.T
Lat_QPF = Lat_QPF.T
lon_QPF_G = np.append(lon_QPF , 123.5125) - 0.00625
lat_QPF_G = np.append(lat_QPF , 27.0125) - 0.00625
Lon_QPF_G , Lat_QPF_G = np.meshgrid(lon_QPF_G , lat_QPF_G)
Lon_QPF_G = Lon_QPF_G.T
Lat_QPF_G = Lat_QPF_G.T
nan_array1 = np.empty([1 , 561])
nan_array2 = np.empty([442 , 1])
nan_array1[:] = np.nan
nan_array2[:] = np.nan
data_G = np.hstack((np.vstack((data , nan_array1)) , nan_array2)).T

num_lon = len(lon_QPF)
num_lat = len(lat_QPF)

colors = ['#635273','#736384','#9c9c9c','#00ce00','#00ad00','#009400','#ffff00','#e7c600','#ff9400','#ff6363',
          '#ff0000','#ce0000','#ff00ff','#9c31ce','#ffffff']
levels = [0 , 1 , 2 , 5 , 10 , 15 , 20 , 30 , 40 , 50 , 80 , 100 , 150 , 200 , 250 , 300]
ticks = [0 , 1 , 2 , 5 , 10 , 15 , 20 , 30 , 40 , 50 , 80 , 100 , 150 , 200 , 250]
tickLabels = ticks

plt.close()
fig , ax = plt.subplots(figsize = [8 , 6])
# ax.set_xlim([121.40 , 121.75])
# ax.set_ylim([24.90 , 25.25])
ax.set_xlim([120 , 121.25])
ax.set_ylim([22.25 , 23.50])
cmap = ListedColormap(colors)
norm = BoundaryNorm(levels , cmap.N)
PC = ax.pcolormesh(Lon_QPF_G , Lat_QPF_G , data , shading = 'flat' , cmap = cmap , norm = norm , alpha = 1)
gs_KHH.plot(ax = ax , alpha = 0.4)
gs_KHH_warn.boundary.plot(ax = ax , color = 'k' , linewidth = 0.2)
# for cnt_warn in np.arange(0 , num_warn):
#     for cnt_lon in np.arange(0 , num_lon):
#         for cnt_lat in np.arange(0 , num_lat):
#             if gs_KHH_warn[cnt_warn].contains(gm.Point((Lon_QPF[cnt_lon , cnt_lat] , Lat_QPF[cnt_lon , cnt_lat]))):
#                 plt.scatter(Lon_QPF[cnt_lon , cnt_lat] , Lat_QPF[cnt_lon , cnt_lat] , marker = 'o' , s = 0.1 , c = 'k' , alpha = 0.8)
#                 break
#     else:
#         continue
#     break
cbar = plt.colorbar(PC , orientation = 'vertical' , ticks = ticks)
cbar.ax.set_yticklabels(tickLabels)
cbar.ax.tick_params(labelsize = 12)
cbar.set_label('mm/hr' , size = 12)
fig.savefig('./pic/KHC/test2.png' , dpi = 200)
# plt.show()

########## Projection Converter ##########
# TWD97 = Proj(init = 'epsg:3824')
# TWD97_TM2 = Proj(init = 'epsg:3826')
# WGS84 = Proj(init = 'epsg:4326')
# lon , lat = TWD97(121.3923331 , 25.1498352)
# lon_new , lat_new = pyproj.transform(TWD97 , TWD97_TM2 , lon , lat)
# lon_new_new , lat_new_new = pyproj.transform(TWD97_TM2 , WGS84 , lon_new , lat_new)
# # print(lon , lat)
# # print(lon_new , lat_new)
# # print(lon_new_new , lat_new_new)

# lonTPE_TWD97 , latTPE_TWD97 = shpdata_county.geometry[6].exterior.coords.xy

# fd_file = os.open(inPath , os.O_RDONLY)
# sz_file = os.stat(inPath).st_size
# size = os.read(fd_file , sz_file)
# print(size)