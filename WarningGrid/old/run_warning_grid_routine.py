########################################
##### run_warning_grid_routine.py ######
######## Author: Wei-Jhih Chen #########
########## Update: 2022/05/17 ##########
########################################

import os
import csv
import gzip
import datetime as dt
import numpy as np
from datetime import datetime as dtdt
from create_warning_grid import create_warning_grid

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

def main():
    ########## Set Products Name ##########
    agency_name = 'KHC'
    products = ['cb_rain01h_rad_gc' , 'qpfqpe_060min']
    products_abr = ['QPEGC_1H' , 'QPF_1H']
    minute_delay = 7            # Units: minute

    ########## Set Time ##########
    inYear = dt.datetime.strftime(dtdt.now() - dt.timedelta(hours = 8) - dt.timedelta(minutes = minute_delay) , '%Y')
    inMonth = dt.datetime.strftime(dtdt.now() - dt.timedelta(hours = 8) - dt.timedelta(minutes = minute_delay) , '%m')
    inDay = dt.datetime.strftime(dtdt.now() - dt.timedelta(hours = 8) - dt.timedelta(minutes = minute_delay) , '%d')
    inHour = dt.datetime.strftime(dtdt.now() - dt.timedelta(hours = 8) - dt.timedelta(minutes = minute_delay) , '%H')
    inMinute = dt.datetime.strftime(dtdt.now() - dt.timedelta(hours = 8) - dt.timedelta(minutes = minute_delay) , '%M')

    ########## Set Path ##########
    datetime = '20220510.0700'
    # datetime = f'{inYear}{inMonth}{inDay}.{inHour}{inMinute}'
    homeDir = r'C:\Users\wjchen\Documents'
    gridDir = fr'{homeDir}\Qplus\tab'
    gridPath = fr'{gridDir}\{agency_name}_warning_grid_441x561.csv'
    outDir = fr'{homeDir}\Qplus\warning'
    outPath = fr'{outDir}\{agency_name}_warning_grid_{datetime}.txt'

    ########## Check Dirs & Warning Grid File ##########
    if not(os.path.isdir(outDir)):
        os.makedirs(outDir)
        print(fr'Create Directory: {outDir}')

    ########## Read Ranges ##########
    idx_grid_in_area = 1
    idx_area0 = 1
    Sid = []
    Sname = []
    with open(gridPath , newline = '' , encoding = 'utf-8') as fi:
        warning_grid_data = csv.reader(fi)
        next(warning_grid_data)
        for warning_grid in warning_grid_data:
            if int(warning_grid[2]) != idx_grid_in_area:
                Sid = np.append(Sid , sid)
                Sname = np.append(Sname , sname)
                idx_grid_in_area = 1
            
            # if int(warning_grid[2]) != idx_area0:
            #     rng_all = np.append(rng_all , rng_area)
            #     idx_area0 += 1
            sid = warning_grid[0]
            sname = warning_grid[1]

    ########## Write Maximum of Each Product in Warning Grids to File (.csv) ##########
    num_product = len(products)
    for cnt_product in np.arange(0 , num_product):
        inDir = rf'{homeDir}\QPESUMS\grid\{products[cnt_product]}'
        if products[cnt_product] == 'cb_rain01h_rad_gc':
            inFile = f'CB_GC_PCP_1H_RAD.{datetime}.gz'
            time = inFile[17:]
        elif products[cnt_product] == 'qpfqpe_060min':
            inFile = f'qpfqpe_060min.{datetime}.gz'
            time = inFile[14:]

        ##### Read Products #####
        inPath = f'{inDir}\{inFile}'
        data = readMosaic2D(inPath)

        ##### Read Warning Grids #####
        idx_grid_in_area = 1
        idx_area0 = 1
        max = -999
        Sid = []
        Sname = []
        Max = []
        with open(gridPath , newline = '' , encoding = 'utf-8') as fi:
            warning_grid_data = csv.reader(fi)
            next(warning_grid_data)
            for warning_grid in warning_grid_data:
                if int(warning_grid[2]) != idx_grid_in_area:
                    Sid = np.append(Sid , sid)
                    Sname = np.append(Sname , sname)
                    max = -999
                    if data[idx_x , idx_y] > max: max = data[idx_x , idx_y]     # Update the Maximum Data
                    idx_grid_in_area = 1
                if int(warning_grid[0][-3:]) != idx_area0:
                    Max = np.append(Max , max)
                    idx_area0 += 1
                sid = warning_grid[0]
                sname = warning_grid[1]
                idx_x = int(warning_grid[3]) - 1
                idx_y = int(warning_grid[4]) - 1
                if data[idx_x , idx_y] > max: max = data[idx_x , idx_y]     # Update the Maximum Data
                idx_grid_in_area += 1
            Sid = np.append(Sid , sid)
            Sname = np.append(Sname , sname)
            Max = np.append(Max , max)
        if cnt_product == 0:
            Max_all = Max
        else:
            Max_all = np.vstack((Max_all , Max))

    num_sec = np.size(Max_all , 1)
    ########## Output .txt ##########
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        fo.write('Warning from maximum data in warning area\n')
        fo.write(f'Time: {datetime}\n')
        fo.write(f'warning_area    warning_area_code    value    datatype\n')
        for cnt_product in np.arange(0 , num_product):
            for cnt_sec in np.arange(0 , num_sec):
                fo.write(f'{Sname[cnt_sec]}    {Sid[cnt_sec]}    {Max_all[cnt_product , cnt_sec]:.6f}    {products_abr[cnt_product]}\n')

if __name__ == '__main__':
    main()