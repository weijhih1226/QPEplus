########################################
############# write_shp.py #############
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

import csv
import numpy as np
import geopandas as gpd
import shapely.geometry as gm

import gzip

def readMosaic2D(filePath):
    if filePath[-3:] == '.gz':
        file = gzip.GzipFile(mode = 'rb' , fileobj = open(filePath , 'rb'))
    else:
        file = open(filePath , 'rb')

    with file as f:
        bytedata = f.read()
        num_byte = len(bytedata)
        param = np.zeros(20 , dtype = np.int64)
        for cnt_byte_grp in range(20):
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
        for cnt_byte_grp in range(20 , 20 + num_z):
            cnt_byte = cnt_byte_grp * 4
            zht[cnt_byte_grp - 20] = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')

        for cnt_byte_grp in range(20 + num_z , 21 + num_z):
            cnt_byte = cnt_byte_grp * 4
            z_scale = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')

        for cnt_byte_grp in range(21 + num_z , 22 + num_z):
            cnt_byte = cnt_byte_grp * 4
            i_bb_mode = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')

        cnt_byte_grp = 31 + num_z
        num_byte = cnt_byte_grp * 4

        varName = ''
        varUnit = ''
        for cnt_byte in range(num_byte , num_byte + 20):
            varName += chr(bytedata[cnt_byte])
        varName = varName.strip('\x00')
        for cnt_byte in range(num_byte + 20 , num_byte + 26):
            varUnit += chr(bytedata[cnt_byte])
        varUnit = varUnit.strip('\x00')
        
        cnt_byte = num_byte + 26
        var_scale = int.from_bytes(bytedata[cnt_byte : cnt_byte + 4] , byteorder = 'little')
        imissing = int.from_bytes(bytedata[cnt_byte + 4 : cnt_byte + 8] , byteorder = 'little')
        nradars = int.from_bytes(bytedata[cnt_byte + 8 : cnt_byte + 12] , byteorder = 'little')

        cnt_byte = cnt_byte + 12
        mosradar = []
        if nradars != 0:
            for cnt_rad in range(nradars):
                cnt_rad_byte = cnt_byte + cnt_rad * 4
                mosradar.append(chr(bytedata[cnt_rad_byte]) + chr(bytedata[cnt_rad_byte + 1]) + chr(bytedata[cnt_rad_byte + 2]) + chr(bytedata[cnt_rad_byte + 3]))
            idx_byte = cnt_rad_byte + 3
        else:
            idx_byte = cnt_byte

        data = np.empty([num_x , num_y])
        for cnt_z in range(num_z):
            for cnt_y in range(num_y):
                for cnt_x in range(num_x):
                    data[cnt_x , cnt_y] = int.from_bytes(bytedata[idx_byte + 1 : idx_byte + 3] , byteorder = 'little') / var_scale
                    if data[cnt_x , cnt_y] < -90:
                        data[cnt_x , cnt_y] = -999
                    if data[cnt_x , cnt_y] == 16383:
                        data[cnt_x , cnt_y] = -999
                    idx_byte += 2

    data[data == -999] = np.nan
    return data

def write_threshold(item_num , num_code , institution , section_name , stid , stname , threshold , Idx_gs , agency_name , area_type , product_name , homeDir):
    outPath = fr'{homeDir}\threshold\{agency_name}_{area_type}_{product_name}.csv'
    qpegc = qpf = threshold
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        writer = csv.writer(fo)
        writer.writerow(['item_num' , 'num_code' , 'institution' , 'section_name' , 'stid' , 'stname' , 'qpegc' , 'qpf' , 'alarm_level'])
        for cnt_item in Idx_gs:
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , stid[cnt_item] , stname[cnt_item] , qpegc[cnt_item] , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , qpf[cnt_item] , 'PRE-WARNING'])

def main():
    homeDir = r'C:\Users\wjchen\Documents\Tools'
    refPath = rf'{homeDir}\shp\Agency\THB_expy61\thbwarning_Tai61_20220706.0520.txt'
    refPath2 = rf'{homeDir}\shp\Agency\THB_expy61\台61每公里里程座標_TWD67.csv'
    outPath = rf'{homeDir}\shp\Agency\THB_expy61\THB_expy61_TWD67.shp'

    NO_road = np.loadtxt(refPath , usecols = (1 , ) , skiprows = 1 , dtype = str)
    Mileage = np.loadtxt(refPath , usecols = (2 , ) , skiprows = 1 , dtype = str)
    Height = np.loadtxt(refPath , usecols = (5 , ) , skiprows = 1 , dtype = float)
    County = np.loadtxt(refPath , usecols = (9 , ) , skiprows = 1 , dtype = str)
    Agency = np.loadtxt(refPath , usecols = (10 , ) , skiprows = 1 , dtype = str)
    Section = np.loadtxt(refPath , usecols = (11 , ) , skiprows = 1 , dtype = str)
    District = np.loadtxt(refPath , usecols = (12 , ) , skiprows = 1 , dtype = str)
    Village = np.loadtxt(refPath , usecols = (13 , ) , skiprows = 1 , dtype = str)

    with open(refPath2 , 'r' , encoding = 'utf-8') as fi:   
        rows = csv.reader(fi)
        next(rows)
        rows = np.array(list(rows) , dtype = float)
        NO = np.array(rows[: , 0] , dtype = int)
        Lat_TWD97 = rows[: , 1]
        Lon_TWD97 = rows[: , 2]
        Lat_TWD67 = rows[: , 3]
        Lon_TWD67 = rows[: , 4]

    num_x , num_y = 441 , 561
    dx , dy = 0.0125 , 0.0125
    lon_start , lat_start = 118.0 , 20.0
    lon_end = lon_start + (num_x - 1) * dx
    lat_end = lat_start + (num_y - 1) * dy
    scale = 100000
    lon = np.arange(lon_start * scale , (lon_end + dx) * scale , dx * scale) / scale
    lat = np.arange(lat_start * scale , (lat_end + dy) * scale , dy * scale) / scale
    lonG = np.arange((lon_start - dx / 2) * scale , (lon_end + dx * 3 / 2) * scale , dx * scale) / scale
    latG = np.arange((lat_start - dy / 2) * scale , (lat_end + dy * 3 / 2) * scale , dy * scale) / scale
    Lat , Lon = np.meshgrid(lat , lon)
    LatG , LonG = np.meshgrid(latG , lonG)

    # TWD67
    X_Num = []
    Y_Num = []
    geometry = []
    for cnt_p in range(len(Lat_TWD67)):
        dist = (Lat_TWD67[cnt_p] - Lat) ** 2 + (Lon_TWD67[cnt_p] - Lon) ** 2
        dist_argmin = np.argmin(dist)
        x_num = dist_argmin // dist.shape[1]
        y_num = dist_argmin % dist.shape[1]
        X_Num.append(x_num)
        Y_Num.append(y_num)
        geometry.append(gm.Polygon([(LonG[x_num , y_num] , LatG[x_num , y_num]) , (LonG[x_num + 1 , y_num] , LatG[x_num + 1 , y_num]) , (LonG[x_num + 1 , y_num + 1] , LatG[x_num + 1 , y_num + 1]) , (LonG[x_num , y_num + 1] , LatG[x_num , y_num + 1])]))
    geometry = gpd.GeoSeries(geometry , crs = 'EPSG:3821')

    gdf = gpd.GeoDataFrame({'NO' : NO , 'NO_road' : NO_road , 'Mileage' : Mileage , 'Lat_TWD97' : Lat_TWD97 , 'Lon_TWD97' : Lon_TWD97 , 
    'Lat_TWD67' : Lat_TWD67 , 'Lon_TWD67' : Lon_TWD67 , 'Height' : Height , 
    'County' : County , 'Agency' : Agency , 'Section' : Section , 'District' : District , 'Village' : Village , 'x_num' : X_Num , 'y_num' : Y_Num , 'geometry' : geometry})
    gdf.to_file(outPath , encoding = 'utf-8')
    print(f'Create shapefiles: {outPath}!')
    print(gdf)

    products_abr = ['QPE1H_grid' , 'QPE1H_ave' , 'QPE1H_max']
    num_product = len(products_abr)
    num_sec = len(gdf)

    datetime = '20220726.0100'
    inPath = fr'C:\Users\wjchen\Documents\Qplus\ref\CB_GC_PCP_1H_RAD.{datetime}.gz'
    outPath = fr'C:\Users\wjchen\Documents\Qplus\warning\THB_expy61_warning_grid_{datetime}.txt'
    outPath2 = fr'C:\Users\wjchen\Documents\Qplus\warning\THB_expy61_warning_grid_2_{datetime}.txt'
    data = readMosaic2D(inPath)

    Sname = []
    Sid = []
    QPE1H_grid = []
    QPE1H_ave = []
    QPE1H_max = []
    for cnt_sec in np.arange(0 , num_sec):
        sname = f'{gdf.NO_road[cnt_sec]}-{gdf.Mileage[cnt_sec]}'
        sid = f'THB61{gdf.NO[cnt_sec]:03d}'
        qpe1h_grid = data[gdf.x_num[cnt_sec] , gdf.y_num[cnt_sec]]
        qpe1h_ave = np.mean(data[gdf.x_num[cnt_sec] - 2 : gdf.x_num[cnt_sec] + 3 , gdf.y_num[cnt_sec] - 2 : gdf.y_num[cnt_sec] + 3])
        qpe1h_max = np.max(data[gdf.x_num[cnt_sec] - 2 : gdf.x_num[cnt_sec] + 3 , gdf.y_num[cnt_sec] - 2 : gdf.y_num[cnt_sec] + 3])

        Sname = np.append(Sname , sname)
        Sid = np.append(Sid , sid)
        QPE1H_grid = np.append(QPE1H_grid , qpe1h_grid)
        QPE1H_ave = np.append(QPE1H_ave , qpe1h_ave)
        QPE1H_max = np.append(QPE1H_max , qpe1h_max)

    ########## Output .txt ##########
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        fo.write('Warning from maximum data in warning area\n')
        fo.write(f'Time: {datetime}\n')
        fo.write(f'warning_area\twarning_area_code\tvalue\tdatatype\n')
        for cnt_sec in np.arange(0 , num_sec):
            fo.write(f'{Sname[cnt_sec]}\t{Sid[cnt_sec]}\t{QPE1H_grid[cnt_sec]:.4f}\t{products_abr[0]}\n')
        for cnt_sec in np.arange(0 , num_sec):
            fo.write(f'{Sname[cnt_sec]}\t{Sid[cnt_sec]}\t{QPE1H_ave[cnt_sec]:.4f}\t{products_abr[1]}\n')
        for cnt_sec in np.arange(0 , num_sec):
            fo.write(f'{Sname[cnt_sec]}\t{Sid[cnt_sec]}\t{QPE1H_max[cnt_sec]:.4f}\t{products_abr[2]}\n')

    # padding = ' '
    # with open(outPath2 , 'w' , newline = '' , encoding = 'utf-8') as fo:
    #     # fo.write('{:>4}{:>15}{:>12}'.format('NO' , ))
    #     fo.write(f'{"NO":{padding}>{4}}{"Warning_area":{padding}>{15}}{"QPE1H_grid":{padding}>{12}}{"QPE1H_ave":{padding}>{12}}{"QPE1H_max":{padding}>{12}}{"County":{padding}>{8}}{"Agency":{padding}>{18}}{"Section":{padding}>{12}}{"District":{padding}>{10}}{"Village":{padding}>{10}}\n')
    #     for cnt_sec in np.arange(0 , num_sec):
    #         fo.write(f'{NO[cnt_sec]:4d}{Sname[cnt_sec]:{padding}>{14}}{QPE1H_grid[cnt_sec]:12.4f}{QPE1H_ave[cnt_sec]:12.4f}{QPE1H_max[cnt_sec]:12.4f}{County[cnt_sec]:{padding}>{5}}{Agency[cnt_sec]:{padding}>{10}}{Section[cnt_sec]:{padding}>{7}}{District[cnt_sec]:{padding}>{7}}{Village[cnt_sec]:{padding}>{7}}\n')

if __name__ == '__main__':
    main()