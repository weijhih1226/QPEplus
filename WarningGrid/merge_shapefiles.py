########################################
######### merge_shapefiles.py ##########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/10/24 ##########
########################################

import numpy as np
import geopandas as gpd
from pathlib import Path

def THB_bridge_20221024(inPath1 , inPath2 , outPath):
    '''
    Test
    '''
    shpData1 = gpd.read_file(inPath1)
    bridge_WGS84 = []
    bridge_TWD97_TM2 = []
    for cnt_gs in range(len(shpData1)):
        bridge_x_WGS84 , bridge_y_WGS84 = shpData1.geometry[cnt_gs].coords.xy
        bridge_WGS84.append([bridge_x_WGS84[0] , bridge_y_WGS84[0]])
    bridgeData = gpd.GeoDataFrame(bridge_WGS84 , columns = ['br_x_WGS84' , 'br_y_WGS84'])
    shpData1['br_x_WGS84'] = bridgeData['br_x_WGS84']
    shpData1['br_y_WGS84'] = bridgeData['br_y_WGS84']

    shpData1 = shpData1.to_crs(3826)
    
    for cnt_gs in range(len(shpData1)):
        bridge_x_TWD97_TM2 , bridge_y_TWD97_TM2 = shpData1.geometry[cnt_gs].coords.xy
        bridge_TWD97_TM2.append([bridge_x_TWD97_TM2[0] , bridge_y_TWD97_TM2[0]])
    bridgeData = gpd.GeoDataFrame(bridge_TWD97_TM2 , columns = ['br_x_TWD97_TM2' , 'br_y_TWD97_TM2'])
    shpData1['br_x_TWD97_TM2'] = bridgeData['br_x_TWD97_TM2']
    shpData1['br_y_TWD97_TM2'] = bridgeData['br_y_TWD97_TM2']

    shpData2 = gpd.read_file(inPath2)[::-1].reset_index(drop = True).to_crs(3826)

    outShpData = shpData1.sjoin(shpData2 , how = "right")
    outShpData.to_file(outPath , encoding = 'utf-8')

def THB_bridge_20221201(inPath1 , inPath2 , outPath):
    '''
    Test
    '''
    shpData1 = gpd.read_file(inPath1)
    bridge_WGS84 = []
    bridge_TWD97_TM2 = []
    for cnt_gs in range(len(shpData1)):
        bridge_x_WGS84 , bridge_y_WGS84 = shpData1.geometry[cnt_gs].coords.xy
        bridge_WGS84.append([bridge_x_WGS84[0] , bridge_y_WGS84[0]])
    bridgeData = gpd.GeoDataFrame(bridge_WGS84 , columns = ['br_x_WGS84' , 'br_y_WGS84'])
    shpData1['br_x_WGS84'] = bridgeData['br_x_WGS84']
    shpData1['br_y_WGS84'] = bridgeData['br_y_WGS84']

    shpData1 = shpData1.to_crs(3826)
    
    for cnt_gs in range(len(shpData1)):
        bridge_x_TWD97_TM2 , bridge_y_TWD97_TM2 = shpData1.geometry[cnt_gs].coords.xy
        bridge_TWD97_TM2.append([bridge_x_TWD97_TM2[0] , bridge_y_TWD97_TM2[0]])
    bridgeData = gpd.GeoDataFrame(bridge_TWD97_TM2 , columns = ['br_x_TWD97_TM2' , 'br_y_TWD97_TM2'])
    shpData1['br_x_TWD97_TM2'] = bridgeData['br_x_TWD97_TM2']
    shpData1['br_y_TWD97_TM2'] = bridgeData['br_y_TWD97_TM2']

    shpData2 = gpd.read_file(inPath2)[::-1].reset_index(drop = True).to_crs(3826)

    outShpData = shpData1.sjoin(shpData2 , how = "right")

    # 2022/12/01 修改「臺」至「台」；「第X區養護工程處」至「第X區工程處」
    for cnt_rut in range(len(outShpData['路線'])):
        outShpData['路線'][cnt_rut] = outShpData['路線'][cnt_rut].replace('臺' , '台')
        outShpData['養護單'][cnt_rut] = outShpData['養護單'][cnt_rut][:7] + outShpData['養護單'][cnt_rut][9:]

    outShpData.to_file(outPath , encoding = 'utf-8')

def main():
    inDir = 'Agency'
    inAgency = 'THB'
    inType = 'bridge'
    inFilename1 = '風險值20橋梁'                # EPSG: 4326 (WGS84)
    inFilename2 = '風險值20_集水區'             # EPSG: 3826 (TWD97-TM2, lon0=121)
    outFilename = '風險值20橋梁_集水區_合併'    # EPSG: 3826 (TWD97-TM2, lon0=121)

    homeDir = Path(r'C:\Users\wjchen\Documents\QPEplus\shp')
    inPath1 = homeDir / inDir / f'{inAgency}_{inType}' / f'{inFilename1}.shp'
    inPath2 = homeDir / inDir / f'{inAgency}_{inType}' / f'{inFilename2}.shp'
    outDir = homeDir / inDir / f'{inAgency}_{inType}'
    outPath = outDir / f'{outFilename}.shp'

    # THB_bridge_20221024(inPath1 , inPath2 , outPath)
    THB_bridge_20221201(inPath1 , inPath2 , outPath)

if __name__ == '__main__':
    main()