########################################
########### write_secinfo.py ###########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/10/26 ##########
########################################

import pandas as pd
import geopandas as gpd
from pathlib import Path

def rename(gdf , names):
    gdf.rename(columns = names , inplace = True)
    return gdf

def slice(gdf , slices):
    eles = list(slices.keys())
    fmts = list(slices.values())
    for cnt_s in range(len(slices)):
        gdf_eles = list(gdf[eles[cnt_s]])
        gdf[eles[cnt_s]] = eval(f'[ele[{fmts[cnt_s]}] for ele in gdf_eles]')
    return gdf

def merge(gdf , infos):
    titles = list(infos.keys())
    contents = [''] * len(gdf)
    for title in titles:
        strArray = []
        elements = infos[title]['Element']
        joins = infos[title]['Join']
        for cnt_e in range(len(elements)):
            strArray.append(list(gdf[elements[cnt_e]]))

        for cnt_i in range(len(gdf)):
            contents[cnt_i] = ''.join([f'{joins[cnt_e]}{strArray[cnt_e][cnt_i]}' for cnt_e in range(len(elements))]) + joins[-1]
        gdf[title] = contents
    return gdf

def write_secinfo(outPath , gdf , secID_head , secName_title , secInfo_title):
    df = {}
    df['Section_ID'] = [secID_head + f'{cnt_i + 1:03d}' for cnt_i in range(len(gdf))]
    df['Section_Name'] = gdf[secName_title]
    infoIn_title = list(secInfo_title.keys())
    infoOut_title = list(secInfo_title.values())
    for cnt_df in range(len(secInfo_title)):
        df[infoOut_title[cnt_df]] = gdf[infoIn_title[cnt_df]]

    pd.DataFrame(df).to_csv(outPath , index = False)

def main():
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

    homeDir = Path(r'C:\Users\wjchen\Documents\Tools\QPEplus\WarningGrid')
    inDir = homeDir.parent.parent/'shp'/'TWD67'/'Agency'/f'{agencyName}_{areaType}'
    outDir = homeDir/'static'/'secinfo'
    inPath = inDir/f'{inFile}'
    outPath = outDir/f'{agencyName}_{areaType}_secinfo.csv'

    if not(outDir.is_dir()):
        outDir.mkdir(parents = True)
        print(fr'Create Directory: {outDir}')
    
    gdf = gpd.read_file(inPath , encoding = 'utf-8')
    gdf = slice(gdf , secInfo_slice)
    gdf = merge(gdf , secInfo_merge)
    write_secinfo(outPath , gdf , secID_head , secName_title , secInfo_output)

if __name__ == '__main__':
    main()