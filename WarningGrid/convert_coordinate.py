########################################
######## convert_coordinate.py #########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/11/01 ##########
########################################

import numpy as np
import geopandas as gpd
from pathlib import Path
from shapely import geometry as gm

# inDir = 'taiwan_county'
# inDir = 'taiwan_town'
# inDir = 'taiwan_village'
# inFilename = 'COUNTY_MOI_1090820'
# inFilename = 'TOWN_MOI_1091016'
# inFilename = 'VILLAGE_MOI_1110426'
# outProj = 'WGS84'
# outExt = 'json'
inDir = 'Agency'
inAgency = 'THB'
inType = 'bridge'
inFilename = '風險值20橋梁_集水區_合併'
outProj = 'TWD67'
outExt = 'shp'

homeDir = Path(r'C:\Users\wjchen\Documents\QPEplus\shp')
inPath = homeDir/inDir/f'{inAgency}_{inType}'/f'{inFilename}.shp'
outDir = homeDir/outProj/inDir/f'{inAgency}_{inType}'
outPath = outDir/f'{inFilename}.{outExt}'

########## Grid Information ##########
# WGS84-Longlat (EPSG:4326)
# TWD97-Longlat (EPSG:3824)
# TWD67-Longlat (EPSG:3821)
# TWD97-TM2, lon0=121 (EPSG:3826)
# TWD97-TM2, lon0=119 (EPSG:3825)
# TWD67-TM2, lon0=121 (EPSG:3828)
# TWD67-TM2, lon0=119 (EPSG:3827)

def TWD67_TM2_to_TWD97_TM2_xy(x67 , y67):
    '''
    Simple manual convertion might have 
    several meters bias!

    From: TWD67-TM2, lon0=121 (EPSG:3828)
    To: TWD97-TM2, lon0=121 (EPSG:3826)
    '''
    A = 0.00001549
    B = 0.000006521
    x97 = x67 + 807.8 + A * x67 + B * y67
    y97 = y67 - 248.6 + A * y67 + B * x67
    return x97 , y97

def TWD97_TM2_to_TWD67_TM2_xy(x97 , y97):
    '''
    Simple manual convertion might have 
    several meters bias!

    From: TWD97-TM2, lon0=121 (EPSG:3826)
    To: TWD67-TM2, lon0=121 (EPSG:3828)
    '''
    A = 0.00001549
    B = 0.000006521
    x67 = x97 - 807.8 - A * x97 - B * y97
    y67 = y97 + 248.6 - A * y97 - B * x97
    return x67 , y67

def TWD97_TM2_to_TWD67_TM2(gs):
    '''
    Simple manual convertion might have 
    several meters bias!

    From: TWD97-TM2, lon0=121 (EPSG:3826)
    To: TWD67-TM2, lon0=121 (EPSG:3828)
    '''
    gs_new = []
    for cnt_gs in range(len(gs)):
        gs_type = gs[cnt_gs].geom_type
        if gs_type == 'MultiPolygon':
            gs_plg = []
            for cnt_pl in range(len(gs[cnt_gs].geoms)):
                x97 , y97 = np.array(gs[cnt_gs].geoms[cnt_pl].exterior.coords.xy)
                x67 , y67 = TWD97_TM2_to_TWD67_TM2_xy(x97 , y97)
                gs_plg.append(gm.Polygon(zip(x67 , y67)))
            gs_plg = gm.MultiPolygon(gs_plg)
        elif gs_type == 'Point':
            x97 , y97 = np.array(gs[cnt_gs].coords.xy)
            x67 , y67 = TWD97_TM2_to_TWD67_TM2_xy(x97 , y97)
            gs_plg = gm.Point(x67 , y67)
        else:
            x97 , y97 = np.array(gs[cnt_gs].exterior.coords.xy)
            x67 , y67 = TWD97_TM2_to_TWD67_TM2_xy(x97 , y97)
            gs_plg = gm.Polygon(zip(x67 , y67))
        gs_new.append(gs_plg)
    return gs_new

def extract_point(gs , int):
    gs_new = []
    for cnt_gs in range(len(gs)):
        gs_type = gs[cnt_gs].geom_type
        if gs_type == 'MultiPolygon':
            gs_plg = []
            for cnt_pl in range(len(gs[cnt_gs].geoms)):
                x , y = np.array(gs[cnt_gs].geoms[cnt_pl].exterior.coords.xy)
                gs_plg.append(gm.Polygon(zip(x[::int] , y[::int])))
            gs_plg = gm.MultiPolygon(gs_plg)
        elif gs_type == 'Point':
            x , y = np.array(gs[cnt_gs].coords.xy)
            gs_plg = gm.Point(x[::int] , y[::int])
        else:
            x , y = np.array(gs[cnt_gs].exterior.coords.xy)
            gs_plg = gm.Polygon(zip(x[::int] , y[::int]))
        gs_new.append(gs_plg)
    return gs_new

def All_to_TWD97_TM2(gs):
    '''
    From: All (EPSG:Need to be defined)
    To: TWD97-TM2, lon0=121 (EPSG:3826)
    '''
    return gpd.GeoSeries(gs).to_crs(3826)

def TWD97_L_to_TWD97_TM2(gs):
    '''
    From: TWD97-Longlat (EPSG:3824)
    To: TWD97-TM2, lon0=121 (EPSG:3826)
    '''
    return gpd.GeoSeries(gs , crs = 3824).to_crs(3826)

def TWD97_L_to_WGS84_L(gs):
    '''
    From: TWD97-Longlat (EPSG:3824)
    To: WGS84-Longlat (EPSG:4326)
    '''
    return gpd.GeoSeries(gs , crs = 3824).to_crs(4326)

def TWD67_TM2_to_TWD67_L(gs):
    '''
    From: TWD67-TM2, lon0=121 (EPSG:3828)
    To: TWD67-Longlat (EPSG:3821)
    '''
    return gpd.GeoSeries(gs , crs = 3828).to_crs(3821)

def main():
    if not(outDir.is_dir()):
        outDir.mkdir(parents = True)
        print(f'Create Directory: {outDir}')

    shpData = gpd.read_file(inPath)
    # shpData = gpd.read_file(inPath , encoding = 'utf-8')

    ##### Output Shapefiles (TWD67-Longlat) #####
    gs_old = All_to_TWD97_TM2(shpData.geometry)     # To TWD97-TM2
    # gs_old = TWD97_L_to_TWD97_TM2(shpData.geometry) # TWD97-Longlat to TWD67-TM2

    gs_new = TWD97_TM2_to_TWD67_TM2(gs_old)         # TWD97-TM2 to TWD67-TM2
    gs_new = TWD67_TM2_to_TWD67_L(gs_new)           # TWD67-TM2 to TWD67-Longlat

    shpData.geometry = gs_new                       # Revise original geometry
    shpData.to_file(outPath , encoding = 'utf-8')   # To file: Shapefiles to shapefiles

    ##### Output Compact GeoJSON (WGS84-Longlat) #####
    # EXTRACT_POINT_INTERVAL = 1
    # gs_new = TWD97_L_to_WGS84_L(shpData.geometry)
    # gs_new = extract_point(gs_new , EXTRACT_POINT_INTERVAL)
    # shpData.geometry = gs_new
    # shpData = shpData.drop(columns=['COUNTYID' , 'COUNTYCODE' , 'COUNTYNAME' , 'COUNTYENG'])
    # shpData = shpData.drop(columns=['TOWNID' , 'TOWNCODE' , 'COUNTYNAME' , 'TOWNNAME' , 'TOWNENG' , 'COUNTYID' , 'COUNTYCODE'])
    # shpData = shpData.drop(columns=['VILLCODE' , 'COUNTYNAME' , 'TOWNNAME' , 'VILLNAME' , 'VILLENG' , 'COUNTYID' , 'COUNTYCODE' , 'TOWNID' , 'TOWNCODE' , 'NOTE'])
    # shpData.to_file(outPath , driver = 'GeoJSON')       # Shapefiles to geojson
    
if __name__ == '__main__':
    main()