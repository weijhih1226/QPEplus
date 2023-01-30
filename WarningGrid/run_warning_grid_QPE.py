########################################
####### run_warning_grid_QPE.py ########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/12/06 ##########
########################################

import os , sys , math , argparse
import numpy as np
import read_radar as rr
import pandas as pd
import datetime as dt
from pathlib import Path
from datetime import datetime as dtdt

AGENCY_NAME = 'THB'
AREA_TYPE = 'bridge'
datetime = '20221019.0200'

USERDIR = Path(r'C:\Users\wjchen')
PROJECTDIR = USERDIR/'Documents'/'QPEplus'
WORKROOT = PROJECTDIR/'WarningGrid'
STATIC_DIR = WORKROOT/'static'
SECINFO_DIR = STATIC_DIR/'secinfo'
GRIDINFO_DIR = STATIC_DIR/'gridinfo'
INDIR = PROJECTDIR/'data'/'grid'
OUTDIR = WORKROOT/'outdata'

PRODUCT_DIR = lambda during: f'cb_rain{during:02d}h_rad_gc'
PRODUCT_FILE = lambda during , datetime: f'CB_GC_PCP_{during}H_RAD.{datetime}.gz'
SECINFO_FILE = lambda agencyName , areaType: f'{agencyName}_{areaType}_secinfo.csv'
GRIDINFO_FILE = lambda agencyName , areaType: f'{agencyName}_{areaType}_gridinfo_441x561.csv'
OUTFILE = lambda agencyName , areaType , datetime: f'{agencyName}_{areaType}_warning_grid_{datetime}.txt'
DATETIME = lambda t , dt_min: dtdt.strftime(t - dt.timedelta(minutes = dt_min) , '%Y%m%d.%H%M')[:-1] + '0'

NUM_X , NUM_Y = 441 , 561
DX , DY = 0.0125 , 0.0125
LON_START , LAT_START = 118.0 , 20.0
SCALE = 1000000

MINUTE_DELAY = 10

def rename(gdf , names):
    gdf.rename(columns = names , inplace = True)
    return gdf

def findNewFile(dir):
    fileLists = os.listdir(dir)
    fileLists.sort(key = lambda fn: os.path.getmtime(Path(dir)/Path(fn))
                   if not(os.path.isdir(Path(dir)/Path(fn))) else 0)
    return fileLists[-1]

def getSecData(data , IdxX , IdxY):
    sData = np.empty(len(IdxX))
    sData.fill(np.nan)
    for cnt_g in range(len(IdxX)):
        sData[cnt_g] = data[IdxX[cnt_g] , IdxY[cnt_g]]
    return sData

def getSecMax(sData , IdxG_in_sec):
    sMax = []
    for cnt_g in range(len(sData)):
        if IdxG_in_sec[cnt_g] == 1:
            sMax.append(sData[cnt_g])
        else:
            if sData[cnt_g] > sMax[-1]:
                sMax[-1] = sData[cnt_g]
    return np.array(sMax)

def getSecAve(sData , IdxG_in_sec):
    idxG_start = np.array((IdxG_in_sec == 1).nonzero())
    idxG_start = np.append(idxG_start , len(sData))
    sAve = []
    for cnt_s in range(len(idxG_start) - 1):
        sAve.append(np.nanmean(sData[idxG_start[cnt_s] : idxG_start[cnt_s + 1]]))
    return np.array(sAve)

def getProduct(product , inDir , during , datetime , productData , dTitle , gridInfo):
    IdxG_in_sec = np.array(gridInfo['Index_Grid_in_Section'])
    IdxX = np.array(gridInfo['Index_of_X']) - 1
    IdxY = np.array(gridInfo['Index_of_Y']) - 1

    for cnt_d in range(len(during)):
        dataPath = inDir/PRODUCT_DIR(during[cnt_d])/PRODUCT_FILE(during[cnt_d] , datetime)
        Radar = rr.readMosaic2D(dataPath)
        data = Radar.getData()

        sData = getSecData(data , IdxX , IdxY)
        if product == 'Max':
            productData[dTitle[cnt_d]] = getSecMax(sData , IdxG_in_sec)
        elif product == 'Ave':
            productData[dTitle[cnt_d]] = getSecAve(sData , IdxG_in_sec)
    return productData

def outputWarningGrid(outPath , datetime , info , data):
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        dTitle = list(data.keys())
        fo.write(f'Time: {datetime}\n')
        fo.write(f'warning_area    warning_area_code    value    datatype\n')
        for cnt_p in range(len(dTitle)):
            for cnt_s in range(len(info)):
                fo.write(f"{info['Section_Name'][cnt_s]}    {info['Section_ID'][cnt_s]}    {data[dTitle[cnt_p]][cnt_s]:.6f}    {dTitle[cnt_p]}\n")
    print(f'Time: {dtdt.now()}, Output File: {outPath}, Mode: LESS')

def outputMoreInfoWarningGrid(outPath , datetime , info , data):
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        iTitle = list(info.keys())
        dTitle = list(data.keys())
        fo.write(f'Time: {datetime}\n')
        fo.write('    '.join(iTitle + dTitle) + '\n')
        for cnt_s in range(len(info)):
            infoStr = [info[it][cnt_s] for it in iTitle]
            dataStr = [f'{data[pt][cnt_s]:.6f}' for pt in dTitle]
            fo.write('    '.join(infoStr + dataStr) + '\n')
    print(f'Time: {dtdt.now()}, Output File: {outPath}, Mode: MORE')

def get_argument(command):
    parser = argparse.ArgumentParser(prog = 'Output Warning Grids of QPE in Sections' , 
                                     description = 'Output the maximum and average values of QPE within those sections \
                                                    of certain area type which defined by given agency. You should input \
                                                    2 arguments: the agency name & the area type; options with the directories \
                                                    of grid- or section-information, input data, or output files, or verbose \
                                                    mode. If you do not specify the directories, defaults would be used.')
    parser.add_argument('agency' , help = 'the agency name')
    parser.add_argument('area' , help = 'the area type')
    parser.add_argument('-v' , '--verbose' , help = 'output products with more information of the sections' , action = 'store_true')
    parser.add_argument('-s' , '--secinfo' , default = SECINFO_DIR , help = 'the directory of section-information files')
    parser.add_argument('-g' , '--gridinfo' , default = GRIDINFO_DIR , help = 'the directory of grid-information files')
    parser.add_argument('-i' , '--input' , default = INDIR , help = 'the directory of input data files')
    parser.add_argument('-o' , '--output' , default = OUTDIR , help = 'the directory of output files')
    parsed_arg = parser.parse_args(command[1:])
    return parsed_arg

def main(argv):
    parsed_arg = get_argument(argv)
    secInfoDir = parsed_arg.secinfo
    gridInfoDir = parsed_arg.gridinfo
    inDir = parsed_arg.input
    outDir = parsed_arg.output
    agencyName = parsed_arg.agency
    areaType = parsed_arg.area
    outMore = parsed_arg.verbose

    secInfoDir = Path(secInfoDir)
    gridInfoDir = Path(gridInfoDir)
    outDir = Path(outDir)/Path(agencyName)
    inDir = Path(inDir)

    product = 'QPEGC'
    duringMax = [1]
    duringAve = [1 , 3 , 6 , 12 , 24 , 72]
    productMax = [f'{product}_{d}H_max' for d in duringMax]
    productAve = [f'{product}_{d}H_ave' for d in duringAve]

    infoTitle = {'Section_ID': 'SECTION_ID' , 
                 'Institution': 'INSTITUTION' , 
                 'Detailed_Name': 'SECTION_NAME' , 
                 'River': 'RIVER'}
    
    secInfoPath = secInfoDir/SECINFO_FILE(agencyName , areaType)
    gridInfoPath = gridInfoDir/GRIDINFO_FILE(agencyName , areaType)
    outPath = outDir/OUTFILE(agencyName , areaType , datetime)

    if not(outDir.is_dir()):
        minute_checkMax = 0
        outDir.mkdir(parents = True)
        print(fr'Create Directory & Current File: {outDir}')
    elif not(os.listdir(outDir)):
        minute_checkMax = 0
        print(fr'Create Current File: {outDir}')
    else:
        dtStart = dtdt.strptime(findNewFile(outDir)[-17:-4] , '%Y%m%d.%H%M').timestamp()
        dtEnd = (dtdt.now() - dt.timedelta(minutes = MINUTE_DELAY)).timestamp()
        minute_checkMax = math.floor((dtEnd - dtStart) / 600) * 10 - 10

    ########## Read Info ##########
    secInfo = pd.read_csv(secInfoPath , encoding = 'utf-8')
    gridInfo = pd.read_csv(gridInfoPath , encoding = 'utf-8')
    
    ########## Get Products ##########
    productData = {}
    productData = getProduct('Max' , inDir , duringMax , datetime , productData , productMax , gridInfo)
    productData = getProduct('Ave' , inDir , duringAve , datetime , productData , productAve , gridInfo)
    secData = pd.DataFrame(productData)
    
    ########## Output ##########
    if outMore:
        secInfoIn = secInfo[infoTitle.keys()]
        secInfoIn = secInfoIn.rename(columns = infoTitle)
        outputMoreInfoWarningGrid(outPath , datetime , secInfoIn , secData)
    else:
        secInfoIn = secInfo[['Section_Name' , 'Section_ID']]
        outputWarningGrid(outPath , datetime , secInfoIn , secData)

if __name__ == '__main__':
    main(sys.argv)