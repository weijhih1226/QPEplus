########################################
########## write_threshold.py ##########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/11/25 ##########
########################################

import csv
import numpy as np
import geopandas as gpd
from pathlib import Path
from write_secinfo import *

THRESHOLD_DEFAULT = 999

def write_thresholdTHBbr(item_num , num_code , institution , section_name , section_name2 , stid , stname , threshold , agency_name , area_type , product_name , homeDir):
    outPath = Path(homeDir)/'static'/'threshold'/fr'{agency_name}_{area_type}_{product_name}.csv'
    qpegc_1h_max = qpegc_1h_ave = threshold
    qpegc_3h_ave = qpegc_6h_ave = qpegc_12h_ave = qpegc_24h_ave = qpegc_72h_ave = np.ones(len(item_num)) * THRESHOLD_DEFAULT
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        writer = csv.writer(fo)
        writer.writerow(['item_num' , 'num_code' , 'institution' , 'section_name' , 'section_name2' , 'stid' , 'stname' , 'QPEGC_1H_max' , 'QPEGC_1H_ave' , 'QPEGC_3H_ave' , 'QPEGC_6H_ave' , 'QPEGC_12H_ave' , 'QPEGC_24H_ave' , 'QPEGC_72H_ave' , 'alarm_level'])
        for cnt_item in range(len(item_num)):
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , stid[cnt_item] , stname[cnt_item] , qpegc_1h_max[cnt_item] , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , qpegc_1h_ave[cnt_item] , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , 'NULL' , qpegc_3h_ave[cnt_item] , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , 'NULL' , 'NULL' , qpegc_6h_ave[cnt_item] , 'NULL' , 'NULL' , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , 'NULL' , 'NULL' , 'NULL' , qpegc_12h_ave[cnt_item] , 'NULL' , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'NULL' , qpegc_24h_ave[cnt_item] , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'NULL' , 'NULL' , qpegc_72h_ave[cnt_item] , 'PRE-WARNING'])

def main():
    productName = 'qpe'
    agencyName = 'THB'
    areaType = 'bridge'
    areaType_abbr = 'br'
    secName_title = '橋梁名'
    secInfo_slice = {'養護單': '4:'}
    secInfo_merge = {'Detailed_Name': {'Element': ['橋梁名' , '路線' , '橋頭里' , '橋頭_1' , '橋尾里' , '橋尾_1'] , 
                                       'Slice': [':' , ':' , ':' , ':-1' , ':' , ':-1'] , 
                                       'Join': ['' , '(' , '' , '+' , '~' , '+' , ')']}}
    secInfo_output = {'養護單': 'Institution' , 
                      'Detailed_Name': 'Detailed_Name' , 
                      '河川___': 'River'}

    inFile = '風險值20橋梁_集水區_合併.shp'
    secID_head = agencyName + areaType_abbr

    homeDir = Path(r'C:\Users\wjchen\Documents\QPEplus\WarningGrid')
    inDir = homeDir.parent/'shp'/'TWD67'/'Agency'/f'{agencyName}_{areaType}'
    outDir = homeDir/'static'/'secinfo'
    inPath = inDir/f'{inFile}'
    outPath = outDir/f'{agencyName}_{areaType}_secinfo.csv'

    if not(outDir.is_dir()):
        outDir.mkdir(parents = True)
        print(fr'Create Directory: {outDir}')
    
    gdf = gpd.read_file(inPath , encoding = 'utf-8')
    gdf = slice(gdf , secInfo_slice)
    gdf = merge(gdf , secInfo_merge)
    df = to_secinfo(gdf , secID_head , secName_title , secInfo_output)


    institution = df['Institution']
    section_name = df['Detailed_Name']
    section_name2 = df['River']
    stid = df['Section_ID']
    stname = df['Section_Name']

    item_num = []
    cnt_item = 0
    for cnt_id in range(len(stid)):
        if stid[cnt_id] not in list(stid[: cnt_id]):
            cnt_item += 1
        item_num.append(f'{cnt_item:03d}')
    
    num_code = []
    cnt_code1 = 0
    cnt_code2 = 1
    for cnt_ins in range(len(institution)):
        if institution[cnt_ins] not in list(institution[: cnt_ins]):
            cnt_code1 += 1
            cnt_code2 = 1
        else:
            cnt_code2 += 1
        num_code.append(f'{cnt_code1:02d}{cnt_code2:02d}')

    thres = 40
    threshold = np.ones(len(item_num)) * thres
    write_thresholdTHBbr(item_num , num_code , institution , section_name , section_name2 , stid , stname , threshold , agencyName , areaType , productName , homeDir)

if __name__ == '__main__':
    main()