########################################
########## write_gridinfo.py ###########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/07/11 ##########
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
from shapely import geometry as gm

def find_nearest_gridpoint(lon_point , lat_point):
    # Input points: TWD67-Longlat (EPSG:3821)
    num_x , num_y = 441 , 561
    dx , dy = 0.0125 , 0.0125
    lon_start , lat_start = 118.0 , 20.0
    lon_end = lon_start + (num_x - 1) * dx
    lat_end = lat_start + (num_y - 1) * dy
    scale = 10000
    lon = np.arange(lon_start * scale , (lon_end + dx) * scale , dx * scale) / scale
    lat = np.arange(lat_start * scale , (lat_end + dy) * scale , dy * scale) / scale
    Lat , Lon = np.meshgrid(lat , lon)

    x_num = []
    y_num = []
    for cnt_p in range(len(lat_point)):
        dist = (lat_point[cnt_p] - Lat) ** 2 + (lon_point[cnt_p] - Lon) ** 2
        dist_argmin = np.argmin(dist)
        x_num.append(dist_argmin // dist.shape[1])
        y_num.append(dist_argmin % dist.shape[1])
    return x_num , y_num

def read_shpTHB(agency_name , area_type , stid_title , shpName , homeDir):
    ########## Descriptions ##########
    # NO , NO_road , Mileage , Lat_TWD97 , Lon_TWD97 , Lat_TWD67 , Lon_TWD67 , Height , County , Agency , Section , District , Village
    # item_num: stid_num
    # num_code: dist_num + idx_in_dist
    # institution: 行政區
    # section_name: 行政區(編號1)
    # stid: agency_name + stid_num
    # stname: 行政區(編號1)
    # threshold: 淹水值
    sort_name = []
    shpPath = fr'{homeDir}\Tools\shp\Agency\{agency_name}_{area_type}\{shpName}'    # TWD67-LatLong
    shpData = gpd.read_file(shpPath , encoding = 'utf-8').sort_values(by = sort_name , ignore_index = True)
    gs = gpd.GeoSeries(shpData.geometry , crs = 'EPSG:3821')

    dist = shpData['Agency']
    sect = shpData['Section']
    sect2 = shpData['County']
    sect3 = shpData['District']
    sect4 = shpData['Village']
    Lat = shpData['Lat_TWD67']
    Lon = shpData['Lon_TWD67']
    x_num , y_num = find_nearest_gridpoint(Lon , Lat)
    xy_num = zip(x_num , y_num)
    
    stid_num = 0
    sect_num = 0
    idx_in_sect = 0
    idx_in_item = 0
    dist_cmp = []
    sect_cmp = []
    item_num = []
    num_code = []
    institution = []
    section_name = []
    section_name2 = []
    section_name3 = []
    section_name4 = []
    stid = []
    stname = []
    Idx_gs = []
    Idx_in_item = []
    for cnt_gs in range(len(gs)):
        idx_in_sect += 1
        if dist[cnt_gs] != dist_cmp or sect[cnt_gs] != sect_cmp:
            sect_num += 1
            idx_in_sect = 1
        stid_num += 1
        idx_in_item = 1
        dist_cmp = dist[cnt_gs]
        sect_cmp = sect[cnt_gs]
        Idx_gs.append(cnt_gs)
        item_num.append(f'{stid_num:03d}')
        num_code.append(f'{sect_num:02d}{idx_in_sect:02d}')
        institution.append(f'{dist[cnt_gs]}')
        section_name.append(f'{sect[cnt_gs]}')
        section_name2.append(f'{sect2[cnt_gs]}')
        section_name3.append(f'{sect3[cnt_gs]}')
        section_name4.append(f'{sect4[cnt_gs]}')
        stid.append(f'{stid_title}{stid_num:03d}')
        stname.append(f'{sect_num:02d}{idx_in_sect:02d}')
        Idx_in_item.append(idx_in_item)
    return item_num , num_code , institution , section_name , section_name2 , section_name3 , section_name4 , stid , stname , xy_num , Idx_in_item , Idx_gs

def read_shpKHC(agency_name , area_type , shpName , homeDir):
    ########## Descriptions ##########
    # OBJECTID_1 , OBJECTID , ID , GRIDCODE , 行政區 , 淹水值 , 編號1 , 參考站 , Shape_Leng , Shape_Le_1 , Shape_Area
    # item_num: stid_num
    # num_code: dist_num + idx_in_dist
    # institution: 行政區
    # section_name: 行政區(編號1)
    # stid: agency_name + stid_num
    # stname: 行政區(編號1)
    # threshold: 淹水值
    sort_name = ['行政區' , '編號1']
    shpPath = fr'{homeDir}\shp\Agency\{agency_name}_{area_type}\{shpName}'    # TWD67-LatLong
    shpData = gpd.read_file(shpPath , encoding = 'utf-8').sort_values(by = sort_name , ignore_index = True)
    gs = gpd.GeoSeries(shpData.geometry , crs = 'EPSG:3821')

    dist = shpData['行政區']
    thres = shpData['淹水值']
    idx_in_dist = shpData['編號1']

    stid_num = 0
    dist_num = 0
    dist_cmp = []
    idx_in_dist_cmp = []
    item_num = []
    num_code = []
    institution = []
    section_name = []
    stid = []
    stname = []
    threshold = []
    idxG_in_item = 0
    # idxG_in_dist = 0
    Idx_gs = []
    IdxG_in_item = []
    # IdxG_in_dist = []
    for cnt_gs in range(len(gs)):
        idxG_in_item += 1
        # idxG_in_dist += 1
        if dist[cnt_gs] != dist_cmp or idx_in_dist[cnt_gs] != idx_in_dist_cmp:
            if dist[cnt_gs] != dist_cmp:
                dist_num += 1
                # idxG_in_dist = 1
            stid_num += 1
            idxG_in_item = 1
            dist_cmp = dist[cnt_gs]
            idx_in_dist_cmp = idx_in_dist[cnt_gs]
            Idx_gs.append(cnt_gs)
        item_num.append(f'{stid_num:03d}')
        num_code.append(f'{dist_num:02d}{int(idx_in_dist[cnt_gs]):02d}')
        institution.append(dist[cnt_gs])
        section_name.append(f'{dist[cnt_gs]}({idx_in_dist[cnt_gs]})')
        stid.append(f'{agency_name}{stid_num:03d}')
        stname.append(f'{dist[cnt_gs]}({idx_in_dist[cnt_gs]})')
        threshold.append(f'{thres[cnt_gs]:.2f}')
        IdxG_in_item.append(idxG_in_item)
        # IdxG_in_dist.append(idxG_in_dist)
    return item_num , num_code , institution , section_name , stid , stname , threshold , gs , IdxG_in_item , Idx_gs

def write_threshold(item_num , num_code , institution , section_name , stid , stname , threshold , Idx_gs , agency_name , area_type , product_name , homeDir):
    outPath = fr'{homeDir}\Qplus\threshold\{agency_name}_{area_type}_{product_name}.csv'
    qpegc = qpf = threshold
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        writer = csv.writer(fo)
        writer.writerow(['item_num' , 'num_code' , 'institution' , 'section_name' , 'stid' , 'stname' , 'qpegc' , 'qpf' , 'alarm_level'])
        for cnt_item in Idx_gs:
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , stid[cnt_item] , stname[cnt_item] , qpegc[cnt_item] , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , qpf[cnt_item] , 'PRE-WARNING'])
            # writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , stid[cnt_item] , stname[cnt_item] , qpegc[cnt_item] , 'NULL' , 'WARNING'])
            # writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , qpf[cnt_item] , 'WARNING'])
            # writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , stid[cnt_item] , stname[cnt_item] , qpegc[cnt_item] , 'NULL' , 'CRITICAL'])
            # writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , qpf[cnt_item] , 'CRITICAL'])

def write_thresholdTHB(item_num , num_code , institution , section_name , section_name2 , section_name3 , section_name4 , stid , stname , threshold , Idx_gs , agency_name , area_type , product_name , homeDir):
    outPath = fr'{homeDir}\Qplus\threshold\{agency_name}_{area_type}_{product_name}.csv'
    qpe1h_grid = qpe1h_ave = qpe1h_max = threshold
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        writer = csv.writer(fo)
        writer.writerow(['item_num' , 'num_code' , 'institution' , 'section_name' , 'section_name2' , 'section_name3' , 'section_name4' , 'stid' , 'stname' , 'qpe1h_grid' , 'qpe1h_ave' , 'qpe1h_max' , 'alarm_level'])
        for cnt_item in Idx_gs:
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , section_name3[cnt_item] , section_name4[cnt_item] , stid[cnt_item] , stname[cnt_item] , qpe1h_grid[cnt_item] , 'NULL' , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , section_name3[cnt_item] , section_name4[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , qpe1h_ave[cnt_item] , 'NULL' , 'PRE-WARNING'])
            writer.writerow([item_num[cnt_item] , num_code[cnt_item] , institution[cnt_item] , section_name[cnt_item] , section_name2[cnt_item] , section_name3[cnt_item] , section_name4[cnt_item] , stid[cnt_item] , stname[cnt_item] , 'NULL' , 'NULL' , qpe1h_max[cnt_item] , 'PRE-WARNING'])

def write_gridinfo(stid , stname , IdxG_in_item , gs , agency_name , area_type , homeDir):
    warning_range = []  # Units: km
    warning_range = sorted(warning_range)
    num_rng = len(warning_range)
    
    num_x = 441
    num_y = 561
    dx = 0.0125
    dy = 0.0125
    lon_start = 118.0
    lon_end = lon_start + (num_x - 1) * dx
    lat_start = 20.0
    lat_end = lat_start + (num_y - 1) * dy
    map_scale = 10000

    lon = np.arange(lon_start * map_scale , (lon_end + dx) * map_scale , dx * map_scale) / map_scale
    lat = np.arange(lat_start * map_scale , (lat_end + dy) * map_scale , dy * map_scale) / map_scale
    Lon , Lat = np.meshgrid(lon , lat)
    Lon = Lon.T
    Lat = Lat.T

    idx_table = np.empty([num_x , num_y])
    idx_table.fill(np.nan)

    outPath = fr'{homeDir}\gridinfo\{agency_name}_{area_type}_gridinfo_441x561.csv'
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        writer = csv.writer(fo)
        writer.writerow(['Section_ID' , 'Section_Name' , 'Index_Grid_in_Section' , 'Index_of_X' , 'Index_of_Y'])
        for cnt_gs in range(len(gs)):
            for cnt_y in range(num_y):
                for cnt_x in range(num_x):
                    if np.isnan(idx_table[cnt_x , cnt_y]):
                        if gs[cnt_gs].contains(gm.Point((Lon[cnt_x , cnt_y] , Lat[cnt_x , cnt_y]))):
                            idx_table[cnt_x , cnt_y] = cnt_gs + 1
                            writer.writerow([stid[cnt_gs] , stname[cnt_gs] , IdxG_in_item[cnt_gs] , cnt_x + 1 , cnt_y + 1])
                            break

def write_gridyaml(section_name , stid , Idx_gs , agency_name , area_type , homeDir):
    ########## Descriptions ##########
    # section_name: 行政區(編號1)
    # stid: agency_name + stid_num
    outPath = fr'{homeDir}\yaml\{agency_name}_{area_type}_gridarea_meta.yaml'
    with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
        for cnt_item in Idx_gs:
            fo.write(f'{section_name[cnt_item]}: {stid[cnt_item]}\n')

def main():
    # agency_name = 'KHC'
    # area_type = 'flood'
    # product_name = 'qpeqpf'
    # shpName = '易淹水預警區位V4.shp'
    agency_name = 'THB'
    area_type = 'expy61'
    stid_title = f'{agency_name}61'
    product_name = 'qpeqpf'
    shpName = 'THB_expy61_TWD67.shp'

    homeDir = r'C:\Users\wjchen\Documents'
    # item_num , num_code , institution , section_name , stid , stname , threshold , gs , IdxG_in_item , Idx_gs = read_shpKHC(agency_name , area_type , shpName , homeDir)
    item_num , num_code , institution , section_name , section_name2 , section_name3 , section_name4 , stid , stname , xy_num , IdxG_in_item , Idx_gs = read_shpTHB(agency_name , area_type , stid_title , shpName , homeDir)
    # Write GridInfo & Yaml
    # write_gridinfo(stid , stname , IdxG_in_item , gs , agency_name , area_type , homeDir)
    # write_gridinfo(stid , stname , IdxG_in_item , xy_num , agency_name , area_type , homeDir)
    # write_gridyaml(section_name , stid , Idx_gs , agency_name , area_type , homeDir)
    # Write Thresholds
    thres = 40
    threshold = np.ones(len(item_num)) * thres
    write_thresholdTHB(item_num , num_code , institution , section_name , section_name2 , section_name3 , section_name4 , stid , stname , threshold , Idx_gs , agency_name , area_type , product_name , homeDir)

if __name__ == '__main__':
    main()