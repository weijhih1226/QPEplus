########################################
############ read_model.py #############
######## Author: Wei-Jhih Chen #########
########## Update: 2022/06/22 ##########
########################################

import gzip
import struct
import netCDF4 as nc
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime as dtdt
from cartopy.io.shapereader import Reader as shprd
from cartopy.feature import ShapelyFeature as shpft
from matplotlib.colors import ListedColormap , BoundaryNorm

def readColorbar(data , varName):
    if varName == 'cv':
        colors = ['#00ffff' , '#00ecff' , '#00daff' , '#00c8ff' , '#00b6ff' , '#00a3ff' , '#0091ff' , '#007fff' , '#006dff' , '#005bff' , 
                  '#0048ff' , '#0036ff' , '#0024ff' , '#0012ff' , '#0000ff' , '#00ff00' , '#00f400' , '#00e900' , '#00de00' , '#00d300' , 
                  '#00c800' , '#00be00' , '#00b400' , '#00aa00' , '#00a000' , '#009600' , '#33ab00' , '#66c000' , '#99d500' , '#ccea00' , 
                  '#ffff00' , '#fff400' , '#ffe900' , '#ffde00' , '#ffd300' , '#ffc800' , '#ffb800' , '#ffa800' , '#ff9800' , '#ff8800' , 
                  '#ff7800' , '#ff6000' , '#ff4800' , '#ff3000' , '#ff1800' , '#ff0000' , '#f40000' , '#e90000' , '#de0000' , '#d30000' , 
                  '#c80000' , '#be0000' , '#b40000' , '#aa0000' , '#a00000' , '#960000' , '#ab0033' , '#c00066' , '#d50099' , '#ea00cc' , 
                  '#ff00ff' , '#ea00ff' , '#d500ff' , '#c000ff' , '#ab00ff' , '#9600ff']
        cmin = 0
        cmax = 66
        levels = np.arange(cmin , cmax + 1)
        ticks = np.arange(cmin , cmax + 1 , 5)
        tickLabels = ticks
        varUnits = 'dBZ'
        data[data < cmin] = np.nan
        data[data > cmax] = cmax
    elif varName == 'prec':
        colors = ['#c1c1c1' , '#99ffff' , '#00ccff' , '#0099ff' , '#0066ff' , '#339900' , '#33ff00' , '#ffff00' , '#ffcc00' , '#ff9900' , 
                  '#ff0000' , '#cc0000' , '#a50000' , '#990099' , '#cc00cc' , '#ff00ff' , '#ffccff']
        cmin = 0.1
        cmax = 500
        levels = [0.1 , 1 , 2 , 6 , 10 , 15 , 20 , 30 , 40 , 50 , 70 , 90 , 110 , 130 , 150 , 200 , 300 , 500]
        ticks = [0.1 , 1 , 2 , 6 , 10 , 15 , 20 , 30 , 40 , 50 , 70 , 90 , 110 , 130 , 150 , 200 , 300]
        tickLabels = ticks
        varUnits = 'mm hr$^{-1}$'
        data[data < cmin] = np.nan
        data[data > cmax] = cmax
    return data , colors , cmin , cmax , levels , ticks , tickLabels , varUnits

def readMosaic2D(filePath , byte_space , type):
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

        if type == 'cv':
            yyyy = int('20' + str(struct.unpack('<L' , bytedata[0 : 4])[0])[:2])
            mm = int(str(struct.unpack('<L' , bytedata[0 : 4])[0])[2:])
            dd = struct.unpack('<L' , bytedata[4 : 8])[0]
            HH = struct.unpack('<L' , bytedata[8 : 12])[0]
            MM = struct.unpack('<L' , bytedata[12 : 16])[0]
            SS = struct.unpack('<L' , bytedata[16 : 20])[0]
            param6 = struct.unpack('<L' , bytedata[20 : 24])[0]

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
        if param_name == '\x00\x00': iproj = 0
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
        varName = struct.unpack('20s' , bytedata[cnt_byte : cnt_byte + 20])[0].decode().strip(byte_space)
        varUnits = struct.unpack('6s' , bytedata[cnt_byte + 20 : cnt_byte + 26])[0].decode().strip(byte_space)
        
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
                    data[cnt_x , cnt_y] = struct.unpack('<h' , bytedata[cnt_byte : cnt_byte + 2])[0] / var_scale
                    if data[cnt_x , cnt_y] < -90:
                        data[cnt_x , cnt_y] = -999
                    if data[cnt_x , cnt_y] == 16383:
                        data[cnt_x , cnt_y] = -999
                    cnt_byte += 2
    data[data == -999] = np.nan
    return num_x , num_y , alon , alat , dx , dy , data

def main():
    byte_space = '\x20'
    # varName = 'cv'
    varName = 'prec'

    homeDir = r'C:\Users\wjchen\Documents'
    inDir = rf'{homeDir}\QPESUMS\model\RWRF\22062406'
    # inDir = rf'{homeDir}\QPESUMS\model\bQPF\22062406'
    # inFile = f'RWRFcv_22062406_f001_22062407.dat'
    # inFile = f'RWRF_22062406_f001_22062407.dat'
    # inFile = f'22062406_001_22062407.bQPF.dat'
    inFile = f'wrfout_d01_2022-06-24_19_00_00'
    inPath = f'{inDir}\{inFile}'
    # outPath = f'{inPath[:-4]}_{varName}.png'
    outPath = f'{inPath}_{varName}.png'
    shpTWNPath = rf'{homeDir}\Qplus\shp\taiwan_county\COUNTY_MOI_1090820.shp'    # TWNcountyTWD97
    shpCHNPath = rf'{homeDir}\Qplus\shp\china\gadm36_CHN_0.shp'                  # China
    shpJPNPath = rf'{homeDir}\Qplus\shp\japan\gadm36_JPN_0.shp'                  # Japan
    shpPHLPath = rf'{homeDir}\Qplus\shp\philippines\gadm36_PHL_0.shp'            # Philippines

    num_x , num_y = 451 , 451
    data = nc.Dataset(inPath)['RAINNC'][:][0]
    print(np.max(data) , np.min(data))
    print(data.shape)

    # num_x , num_y , alon , alat , dx , dy , data = readMosaic2D(inPath , byte_space , varName)
    data , colors , cmin , cmax , levels , ticks , tickLabels , varUnits = readColorbar(data , varName)

    lon_deg2km = 97.64780673871583                                  # Degree to km (Units: km/deg.)
    lat_deg2km = 108.2418909628443                                  # Degree to km (Units: km/deg.)
    num_x = nc.Dataset(inPath).getncattr('WEST-EAST_GRID_DIMENSION')
    num_y = nc.Dataset(inPath).getncattr('SOUTH-NORTH_GRID_DIMENSION')
    num_z = nc.Dataset(inPath).getncattr('BOTTOM-TOP_GRID_DIMENSION')
    dx = nc.Dataset(inPath).getncattr('DX') / 1000 / lon_deg2km     # Units: deg.
    dy = nc.Dataset(inPath).getncattr('DY') / 1000 / lat_deg2km     # Units: deg.
    clon = nc.Dataset(inPath).getncattr('CEN_LON')
    clat = nc.Dataset(inPath).getncattr('CEN_LAT')
    # Lon_G = nc.Dataset(inPath)['XLONG'][0]
    # Lat_G = nc.Dataset(inPath)['XLAT'][0]
    Lon = np.linspace(clon - dx * (num_x - 1) / 2 , clon + dx * (num_x + 1) / 2 , num_x)
    Lat = np.linspace(clat - dy * (num_y - 1) / 2 , clat + dy * (num_y + 1) / 2 , num_y)
    Lat_G , Lon_G = np.meshgrid(Lat , Lon)

    # Lon = (np.arange(alon * 10000 , alon * 10000 + (num_x + 1) * dx * 10000 , dx * 10000) - dx * 5000) / 10000
    # Lat = np.flipud(np.arange(alat * 10000 , alat * 10000 - (num_y + 1) * dy * 10000 , -dy * 10000) + dy * 5000) / 10000
    # Lon_G , Lat_G = np.meshgrid(Lon , Lat)

    cmap = ListedColormap(colors)
    norm = BoundaryNorm(levels , cmap.N)
    shpTWN = shpft(shprd(shpTWNPath).geometries() , ccrs.PlateCarree() , 
                  facecolor = (1 , 1 , 1 , 0) , edgecolor = (0 , 0 , 0 , 1) , linewidth = 1)
    shpCHN = shpft(shprd(shpCHNPath).geometries() , ccrs.PlateCarree() , 
                  facecolor = (1 , 1 , 1 , 0) , edgecolor = (.2 , .2 , .2 , 1) , linewidth = .5)
    shpJPN = shpft(shprd(shpJPNPath).geometries() , ccrs.PlateCarree() , 
                  facecolor = (1 , 1 , 1 , 0) , edgecolor = (.2 , .2 , .2 , 1) , linewidth = .5)
    shpPHL = shpft(shprd(shpPHLPath).geometries() , ccrs.PlateCarree() , 
                  facecolor = (1 , 1 , 1 , 0) , edgecolor = (.2 , .2 , .2 , 1) , linewidth = .5)

    plt.close()
    fig , ax = plt.subplots(figsize = [12 , 10] , subplot_kw = {'projection' : ccrs.PlateCarree()})
    ax.add_feature(shpTWN , zorder = 2)
    ax.add_feature(shpCHN , zorder = 2)
    ax.add_feature(shpJPN , zorder = 2)
    ax.add_feature(shpPHL , zorder = 2)
    PC = ax.pcolormesh(Lon_G , Lat_G , data.T , shading = 'flat' , cmap = cmap , norm = norm , alpha = 1 , zorder = 1)
    cbar = plt.colorbar(PC , orientation = 'vertical' , ticks = ticks)
    cbar.ax.set_yticklabels(tickLabels)
    cbar.ax.tick_params(labelsize = 12)
    cbar.set_label(varUnits , rotation = 0 , labelpad = -20 , y = 1.03 , size = 12)
    fig.savefig(outPath , dpi = 200)

if __name__ == '__main__':
    main()