########################################
########## write_gridinfo.py ###########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/10/26 ##########
########################################

import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely import geometry as gm

NUM_X , NUM_Y = 441 , 561
DX , DY = 0.0125 , 0.0125
LON_START , LAT_START = 118.0 , 20.0
SCALE = 1000000

def create_gridmap(num_x , num_y , dx , dy , lon_start , lat_start , scale):
    lon_end = lon_start + (num_x - 1) * dx
    lat_end = lat_start + (num_y - 1) * dy
    lon = np.arange(lon_start * scale , (lon_end + dx) * scale , dx * scale) / scale
    lat = np.arange(lat_start * scale , (lat_end + dy) * scale , dy * scale) / scale
    return np.meshgrid(lat , lon)

def write_gridinfo(outPath , gdf , lonG , latG , secID_head , secName_title):
    secID = []
    secName = []
    IdxG_in_sec = []
    IdxX = []
    IdxY = []
    for cnt_gs in range(len(gdf)):
        idxG_in_sec = 0
        for cnt_y in range(NUM_Y):
            for cnt_x in range(NUM_X):
                if gdf.geometry[cnt_gs].contains(gm.Point((lonG[cnt_x , cnt_y] , latG[cnt_x , cnt_y]))):
                    idxG_in_sec += 1
                    secID.append(secID_head + f'{cnt_gs + 1:03d}')
                    secName.append(gdf[secName_title][cnt_gs])
                    IdxG_in_sec.append(idxG_in_sec)
                    IdxX.append(cnt_x + 1)
                    IdxY.append(cnt_y + 1)
    
    df = {}
    df['Section_ID'] = secID
    df['Section_Name'] = secName
    df['Index_Grid_in_Section'] = IdxG_in_sec
    df['Index_of_X'] = IdxX
    df['Index_of_Y'] = IdxY
    pd.DataFrame(df).to_csv(outPath , index = False)

def main():
    agencyName = 'THB'
    areaType = 'bridge'
    areaType_abbr = 'br'
    secName_select = '橋梁名'
    inFile = '風險值20橋梁_集水區_合併.shp'
    secID_title = agencyName + areaType_abbr

    homeDir = Path(r'C:\Users\wjchen\Documents\Tools\QPEplus\WarningGrid')
    inDir = homeDir.parent.parent/'shp'/'TWD67'/'Agency'/f'{agencyName}_{areaType}'
    outDir = homeDir/'static'/'gridinfo'
    inPath = inDir/f'{inFile}'
    outPath = outDir/f'{agencyName}_{areaType}_gridinfo_441x561.csv'

    if not(outDir.is_dir()):
        outDir.mkdir(parents = True)
        print(fr'Create Directory: {outDir}')
    
    gdf = gpd.read_file(inPath , encoding = 'utf-8')

    LAT , LON = create_gridmap(NUM_X , NUM_Y , DX , DY , LON_START , LAT_START , SCALE)
    write_gridinfo(outPath , gdf , LON , LAT , secID_title , secName_select)

if __name__ == '__main__':
    main()