import csv , gzip , struct
import numpy as np
import geopandas as gpd
from shapely import geometry as gm

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader as shprd
from cartopy.feature import ShapelyFeature as shpft
from matplotlib.colors import ListedColormap , BoundaryNorm

def readMosaic2D(filePath):
    if filePath[-3:] == '.gz':
        file = gzip.GzipFile(mode = 'rb' , fileobj = open(filePath , 'rb'))
    else:
        file = open(filePath , 'rb')

    with file as f:
        bytedata = f.read()
        num_byte = len(bytedata)

        ########## Header ##########
        yyyy = struct.unpack('<L' , bytedata[0 : 4])[0]
        mm = struct.unpack('<L' , bytedata[4 : 8])[0]
        dd = struct.unpack('<L' , bytedata[8 : 12])[0]
        HH = struct.unpack('<L' , bytedata[12 : 16])[0]
        MM = struct.unpack('<L' , bytedata[16 : 20])[0]
        SS = struct.unpack('<L' , bytedata[20 : 24])[0]

        num_x = struct.unpack('<L' , bytedata[24 : 28])[0]
        num_y = struct.unpack('<L' , bytedata[28 : 32])[0]
        num_z = struct.unpack('<L' , bytedata[32 : 36])[0]
        param10 = struct.unpack('<L' , bytedata[36 : 40])[0]
        map_scale = struct.unpack('<L' , bytedata[40 : 44])[0]
        param12 = struct.unpack('<L' , bytedata[44 : 48])[0]
        param13 = struct.unpack('<L' , bytedata[48 : 52])[0]
        param14 = struct.unpack('<L' , bytedata[52 : 56])[0]
        alonalat_scale = struct.unpack('<L' , bytedata[64 : 68])[0]
        alon = struct.unpack('<L' , bytedata[56 : 60])[0] / alonalat_scale
        alat = struct.unpack('<L' , bytedata[60 : 64])[0] / alonalat_scale
        dxdy_scale = struct.unpack('<L' , bytedata[76 : 80])[0]
        dx = struct.unpack('<L' , bytedata[68 : 72])[0] / dxdy_scale
        dy = struct.unpack('<L' , bytedata[72 : 76])[0] / dxdy_scale

        param_name = struct.unpack('2s' , bytedata[39 : 37 : -1])[0].decode()
        if param_name == '  ': iproj = 0
        if param_name == 'PS': iproj = 1
        if param_name == 'LA': iproj = 2
        if param_name == 'ME': iproj = 3
        if param_name == 'LL': iproj = 4

        ########## Z-Direction ##########
        zht = np.zeros(num_z , dtype = int)
        for cnt_group in range(20 , 20 + num_z):
            cnt_byte = cnt_group * 4
            zht[cnt_group - 20] = struct.unpack('<L' , bytedata[cnt_byte : cnt_byte + 4])[0]
        for cnt_group in range(20 + num_z , 21 + num_z):
            cnt_byte = cnt_group * 4
            z_scale = struct.unpack('<L' , bytedata[cnt_byte : cnt_byte + 4])[0]
        for cnt_group in range(21 + num_z , 22 + num_z):
            cnt_byte = cnt_group * 4
            i_bb_mode = struct.unpack('<L' , bytedata[cnt_byte : cnt_byte + 4])[0]

        ########## Information ##########
        cnt_group = 31 + num_z
        cnt_byte = cnt_group * 4
        varName = struct.unpack('20s' , bytedata[cnt_byte : cnt_byte + 20])[0].decode().strip('\x00')
        varUnits = struct.unpack('6s' , bytedata[cnt_byte + 20 : cnt_byte + 26])[0].decode().strip('\x00')
        
        cnt_byte += 26
        var_scale = struct.unpack('<L' , bytedata[cnt_byte : cnt_byte + 4])[0]
        imissing = struct.unpack('<l' , bytedata[cnt_byte + 4 : cnt_byte + 8])[0]
        num_rad = struct.unpack('<L' , bytedata[cnt_byte + 8 : cnt_byte + 12])[0]

        ########## Mosaic Radars ##########
        cnt_byte += 12
        mosradar = []
        if num_rad != 0:
            for cnt_rad in range(num_rad):
                mosradar.append(struct.unpack('4s' , bytedata[cnt_byte : cnt_byte + 4])[0].decode())
                cnt_byte += 4

        ########## Data ##########
        data = np.empty([num_x , num_y])
        for cnt_z in range(num_z):
            for cnt_y in range(num_y):
                for cnt_x in range(num_x):
                    data[cnt_x , cnt_y] = struct.unpack('<H' , bytedata[cnt_byte : cnt_byte + 2])[0] / var_scale
                    if data[cnt_x , cnt_y] < -90:
                        data[cnt_x , cnt_y] = -999
                    if data[cnt_x , cnt_y] == 16383:
                        data[cnt_x , cnt_y] = -999
                    cnt_byte += 2
    data[data == -999] = np.nan
    return data

def get_geometry():
    pass

def main():
    homeDir = r'C:\Users\wjchen\Documents\Qplus'
    inPath = r'C:\Users\wjchen\Documents\QPESUMS\grid\cb_rain01h_rad_gc\CB_GC_PCP_1H_RAD.20220510.0700.gz'
    shpTWNPath = rf'{homeDir}\shp\TWD67\taiwan_county\COUNTY_MOI_1090820_TWD67.shp'     # TWNcountyTWD67
    shpWARNPath = rf'{homeDir}\shp\Agency\THB_expy61\THB_expy61_TWD67.shp'

    shpWARNData = gpd.read_file(shpWARNPath , encoding = 'utf-8')
    Lon_TWD67 = shpWARNData['Lon_TWD67']
    Lat_TWD67 = shpWARNData['Lat_TWD67']
    geometry = shpWARNData.geometry

    num_x , num_y = 441 , 561
    dx , dy = 0.0125 , 0.0125
    lon_start , lat_start = 118.0 , 20.0
    lon_end = lon_start + (num_x - 1) * dx
    lat_end = lat_start + (num_y - 1) * dy
    scale = 1000000
    lon = np.arange(lon_start * scale , (lon_end + dx) * scale , dx * scale) / scale
    lat = np.arange(lat_start * scale , (lat_end + dy) * scale , dy * scale) / scale
    lonG = np.arange((lon_start - dx / 2) * scale , (lon_end + dx * 3 / 2) * scale , dx * scale) / scale
    latG = np.arange((lat_start - dy / 2) * scale , (lat_end + dy * 3 / 2) * scale , dy * scale) / scale
    Lat , Lon = np.meshgrid(lat , lon)
    LatG , LonG = np.meshgrid(latG , lonG)

    data = readMosaic2D(inPath)

    shpTWN = shpft(shprd(shpTWNPath).geometries() , ccrs.PlateCarree() , 
                  facecolor = (1 , 1 , 1 , 0) , edgecolor = (0 , 0 , 0 , 1) , linewidth = 1)

    colors = ['#c1c1c1' , '#99ffff' , '#00ccff' , '#0099ff' , '#0066ff' , '#339900' , '#33ff00' , '#ffff00' , '#ffcc00' , '#ff9900' , 
              '#ff0000' , '#cc0000' , '#a50000' , '#990099' , '#cc00cc' , '#ff00ff' , '#ffccff']
    levels = [0.1 , 1 , 2 , 6 , 10 , 15 , 20 , 30 , 40 , 50 , 70 , 90 , 110 , 130 , 150 , 200 , 300 , 500]
    ticks = [0.1 , 1 , 2 , 6 , 10 , 15 , 20 , 30 , 40 , 50 , 70 , 90 , 110 , 130 , 150 , 200 , 300]
    tickLabels = ticks
    varUnits = 'mm hr$^{-1}$'
    cmin = 0.1
    cmax = 500
    data[data < cmin] = np.nan
    data[data > cmax] = cmax

    cmap = ListedColormap(colors)
    norm = BoundaryNorm(levels , cmap.N)
    plt.close()
    fig , ax = plt.subplots(figsize = [12 , 10] , subplot_kw = {'projection' : ccrs.PlateCarree()})
    ax.add_feature(shpTWN , zorder = 2)
    PC = ax.pcolormesh(LonG , LatG , data , shading = 'flat' , cmap = cmap , norm = norm , alpha = 1 , zorder = 1)
    ax.plot(Lon_TWD67 , Lat_TWD67 , zorder = 3)
    geometry.boundary.plot(ax = ax , color = 'k' , linewidth = 0.2 , zorder = 4)
    # ax.axis([lon_start , lon_end , lat_start , lat_end])
    ax.set_xticks(np.arange(lon_start * 10 , lon_end * 10 , 5) / 10)
    ax.set_yticks(np.arange(lat_start * 10 , lat_end * 10 , 5) / 10)
    ax.axis([120 , 120.5 , 23.5 , 24])
    cbar = plt.colorbar(PC , orientation = 'vertical' , ticks = ticks)
    cbar.ax.set_yticklabels(tickLabels)
    cbar.ax.tick_params(labelsize = 12)
    cbar.set_label(varUnits , rotation = 0 , labelpad = -20 , y = 1.03 , size = 12)
    plt.show()

if __name__ == '__main__':
    main()