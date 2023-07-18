########################################
########### Read_Mosaic2D.py ###########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/04/28 ##########
########################################

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

# def readmosaic2D(inPath , data , num_x , num_y):
#     max_size = 11000000
#     size , msg_err = rio_read_file(inPath , max_size)
#     return msg_err
# def rio_read_file(inPath , max_size , msg_err):
#     fd_file = os.open(inPath , os.O_RDONLY)
#     sz_file = os.stat(inPath).st_size
#     if not(os.path.isfile(inPath)):
#         print(f'File Not Found: {inPath}')
#         msg_err = -1
#     if fd_file < 0:
#         print(f'File Not Found: {inPath}')
#         msg_err = -1
#     if sz_file > max_size:
#         print(f'Buffer size too small, real size is: {os.stat(inPath).st_size}')
#         msg_err = -2
#     size = os.read(fd_file , sz_file)
#     msg_err = 0
#     os.close(fd_file)
#     return size , msg_err
# def readhead(bytedata):
#     for i in np.arange(0 , 20):
#         ii = i * 4
#         by4 = bytearray(4)
#         by4[0] = bytedata[0 + ii]
#         by4[1] = bytedata[1 + ii]
#         by4[2] = bytedata[2 + ii]
#         by4[3] = bytedata[3 + ii]

# def by2int4(machine , by4):
#     if machine == 0:

#     else:


#     return int4

products = ['cb_rain01h_rad_gc' , 'qpfqpe_060min']

csv_warning_grid = r'.\tab\TPEwarning_grid_441x561.csv'
shp_TWNcountyTWD97 = r'.\shp\taiwan_county\COUNTY_MOI_1090820.shp'
shp_TWNtownTWD97 = r'.\shp\taiwan_town\TOWN_MOI_1091016.shp'
shp_TWNvillageTWD97 = r'.\shp\taiwan_village\VILLAGE_MOI_1110426.shp'
shp_KHH = r'\\61.56.11.35\qpeplus\001.Qplus客製化\005.縣市\高雄市\易淹水預警區位V4\易淹水預警區位V4.shp'
shpdata_county = gpd.read_file(shp_TWNcountyTWD97 , encoding = 'utf-8')
shpdata_town = gpd.read_file(shp_TWNtownTWD97 , encoding = 'utf-8')
shpdata_village = gpd.read_file(shp_TWNvillageTWD97 , encoding = 'utf-8')
shpdata_KHH = gpd.read_file(shp_KHH , encoding = 'utf-8')

idx_area0 = 0
rng_all = []
datetime = '20220509.0000'
outPath = f'C:/Users/wjchen/Documents/Qplus/warning/TPEwarning_grid_{datetime}.txt'
with open(csv_warning_grid , newline = '') as fi:
    warning_grid_data = csv.reader(fi)
    for warning_grid in warning_grid_data:
        if int(warning_grid[0]) != idx_area0:
            rng_all = np.append(rng_all , rng_area)
            idx_area0 += 1
        rng_area = int(warning_grid[1])
    rng_all = np.append(rng_all , rng_area)
with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
    fo.write('Warning from maximum data in warning area\n')
    fo.write(f'Time: {datetime}\n')
    fo.write(f'datatype\twarning_area\trange<{rng_all[1]:.0f}km\trange<{rng_all[2]:.0f}km\n')

for product in products:
    inDir = f'C:/Users/wjchen/Documents/QPESUMS/grid/{product}/'
    if product == 'cb_rain01h_rad_gc':
        inFile = f'CB_GC_PCP_1H_RAD.{datetime}'
        datatype = 'QPEGC_1H'
        time = inFile[17:]
    elif product == 'qpfqpe_060min':
        inFile = f'qpfqpe_060min.{datetime}'
        datatype = 'QPF_1H'
        time = inFile[14:]

    inPath = f'{inDir}{inFile}'
    with open(inPath , 'rb') as f:
        bytedata = f.read()
        num_byte = len(bytedata)
        param = np.zeros(20 , dtype = np.int64)
        for cnt_byte_grp in np.arange(0 , 20):
            cnt_byte = cnt_byte_grp * 4
            param[cnt_byte_grp] = int.from_bytes(bytedata[3 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[2 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[1 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[0 + cnt_byte].to_bytes(1 , byteorder = 'big') , byteorder = 'big')
            param_name = chr(bytedata[3 + cnt_byte]) + chr(bytedata[2 + cnt_byte])
            if cnt_byte_grp == 9:
                if param_name == '  ': iproj = 0
                if param_name == 'PS': iproj = 1
                if param_name == 'LA': iproj = 2
                if param_name == 'ME': iproj = 3
                if param_name == 'LL': iproj = 4
                param[cnt_byte_grp] = iproj
        
        print(param)
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
            zht[cnt_byte_grp - 20] = int.from_bytes(bytedata[3 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[2 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[1 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[0 + cnt_byte].to_bytes(1 , byteorder = 'big') , byteorder = 'big')

        for cnt_byte_grp in np.arange(20 + num_z , 21 + num_z):
            cnt_byte = cnt_byte_grp * 4
            z_scale = int.from_bytes(bytedata[3 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[2 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[1 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[0 + cnt_byte].to_bytes(1 , byteorder = 'big') , byteorder = 'big')

        for cnt_byte_grp in np.arange(21 + num_z , 22 + num_z):
            cnt_byte = cnt_byte_grp * 4
            i_bb_mode = int.from_bytes(bytedata[3 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[2 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[1 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[0 + cnt_byte].to_bytes(1 , byteorder = 'big') , byteorder = 'big')

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
        var_scale = int.from_bytes(bytedata[3 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[2 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[1 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[0 + cnt_byte].to_bytes(1 , byteorder = 'big') , byteorder = 'big')
        imissing = int.from_bytes(bytedata[7 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[6 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[5 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[4 + cnt_byte].to_bytes(1 , byteorder = 'big') , byteorder = 'big')
        nradars = int.from_bytes(bytedata[11 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[10 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[9 + cnt_byte].to_bytes(1 , byteorder = 'big') + bytedata[8 + cnt_byte].to_bytes(1 , byteorder = 'big') , byteorder = 'big')

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
                    data[cnt_x , cnt_y] = int.from_bytes(bytedata[2 + idx_byte].to_bytes(1 , byteorder = 'big') + bytedata[1 + idx_byte].to_bytes(1 , byteorder = 'big') , byteorder = 'big') / var_scale
                    if data[cnt_x , cnt_y] < -90:
                        data[cnt_x , cnt_y] = -999
                    if data[cnt_x , cnt_y] == 16383:
                        data[cnt_x , cnt_y] = -999
                    idx_byte += 2

    data[data == -999] = np.nan

    idx_area0 = 0
    max_var = -999
    max_var_all = []
    with open(csv_warning_grid , newline = '') as fi:
        warning_grid_data = csv.reader(fi)
        for warning_grid in warning_grid_data:
            if int(warning_grid[0]) != idx_area0:
                max_var_all = np.append(max_var_all , max_var)
                idx_area0 += 1
            idx_area = int(warning_grid[0])
            idx_x = int(warning_grid[2]) - 1
            idx_y = int(warning_grid[3]) - 1
            if data[idx_x , idx_y] > max_var: max_var = data[idx_x , idx_y]
        max_var_all = np.append(max_var_all , max_var)
        print(max_var_all)
    with open(outPath , 'a' , newline = '' , encoding = 'utf-8') as fo:
        fo.write(f'{datatype}\t{max_var_all[0]:.8f}\t{max_var_all[1]:.8f}\t{max_var_all[2]:.8f}\n')

gs_KHH = gpd.GeoSeries(shpdata_KHH.geometry[:] , crs = "EPSG:3824")
gs_TPE_TWD97 = gpd.GeoSeries(shpdata_county.geometry[:] , crs = "EPSG:3824")
gs_TPE_TWD97_TM2 = gs_TPE_TWD97.to_crs("EPSG:3826")
gs_TPE_TWD97_TM2_bf5k = gs_TPE_TWD97_TM2.geometry.buffer(5000)
gs_TPE_TWD97_TM2_bf10k = gs_TPE_TWD97_TM2.geometry.buffer(10000)
gs_TPE_TWD97_bf5k = gs_TPE_TWD97_TM2_bf5k.to_crs("EPSG:3824")
gs_TPE_TWD97_bf10k = gs_TPE_TWD97_TM2_bf10k.to_crs("EPSG:3824")

lons = np.arange(12140 , 12176 , 1) * 0.01
lats = np.arange(2490 , 2526 , 1) * 0.01
Lons , Lats = np.meshgrid(lons , lats)

num_lon = len(lons)
num_lat = len(lats)


lon_QPF = np.arange(1180000 , 1235125 , 125) / 10000
lat_QPF = np.arange(200000 , 270125 , 125) / 10000
Lon_QPF , Lat_QPF = np.meshgrid(lon_QPF , lat_QPF)
Lon_QPF = Lon_QPF.T
Lat_QPF = Lat_QPF.T
lon_QPF_G = np.append(lon_QPF , 123.5125) - 0.00625
lat_QPF_G = np.append(lat_QPF , 27.0125) - 0.00625
Lon_QPF_G , Lat_QPF_G = np.meshgrid(lon_QPF_G , lat_QPF_G)

nan_array1 = np.empty([1 , 561])
nan_array2 = np.empty([442 , 1])
nan_array1[:] = np.nan
nan_array2[:] = np.nan

data_G = np.hstack((np.vstack((data , nan_array1)) , nan_array2)).T
print(np.nanmin(data))

# gdf = gpd.GeoDataFrame(shpdata_county.geometry[6] , crs = 3824)

# print(shpdata_county.geometry[6])
plt.close()
# fig , ax = plt.subplots(figsize = [12 , 10] , subplot_kw = {'projection': crs_epsg})
fig , ax = plt.subplots(figsize = [8 , 6])
# ax.set_xlim([121.40 , 121.75])
# ax.set_ylim([24.90 , 25.25])
ax.set_xlim([117.5 , 124])
ax.set_ylim([19.5 , 27.5])
PC = ax.pcolormesh(Lon_QPF_G , Lat_QPF_G , data_G)
# gs_TPE_TWD97_bf10k.plot(ax = ax , alpha = 0.2)
# gs_TPE_TWD97_bf5k.plot(ax = ax , alpha = 0.2)
# gs_TPE_TWD97.plot(ax = ax , alpha = 0.2)
gs_KHH.plot(ax = ax , alpha = 0.2)
for cnt_lon in np.arange(0 , num_lon):
    for cnt_lat in np.arange(0 , num_lat):
        if gs_TPE_TWD97_bf10k[0].contains(gm.Point((Lons[cnt_lon , cnt_lat] , Lats[cnt_lon , cnt_lat]))):
            plt.scatter(Lons[cnt_lon , cnt_lat] , Lats[cnt_lon , cnt_lat] , marker = 'o' , s = 0.1 , c = 'k' , alpha = 0.8)
cbar = plt.colorbar(PC , orientation = 'vertical')
fig.savefig('./test1.png' , dpi = 200)
# plt.show()


    
plt.close()
fig2 , ax2 = plt.subplots(figsize = [8 , 6])
ax2.set_xlim([121.40 , 121.75])
ax2.set_ylim([24.90 , 25.25])
gs_TPE_TWD97.plot(ax = ax2)
with open(csv_warning_grid , newline = '') as fi:
    warning_grid_data = csv.reader(fi)
    for warning_grid in warning_grid_data:
        idx_x = int(warning_grid[2]) - 1
        idx_y = int(warning_grid[3]) - 1
        plt.scatter(Lon_QPF[idx_x , idx_y] , Lat_QPF[idx_x , idx_y] , marker = 'o' , s = 0.1 , c = 'k' , alpha = 0.8)
        if data[idx_x , idx_y] > 100:
            plt.scatter(Lon_QPF[idx_x , idx_y] , Lat_QPF[idx_x , idx_y] , marker = 'o' , s = 2 , c = 'k' , alpha = 0.8)
fig2.savefig('./test2.png' , dpi = 200)
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