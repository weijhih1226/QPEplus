########################################
######## create_warning_grid.py ########
######## Author: Wei-Jhih Chen #########
########## Update: 2022/05/12 ##########
########################################

import csv
import numpy as np
import geopandas as gpd
from shapely import geometry as gm

agency_name = 'KHC'
shpName = '易淹水預警區位V4'
sort_name = ['行政區' , '編號1']
warning_range = []          # Units: km
idx_shp = 6                 # Index in Shape

homeDir = r'C:\Users\wjchen\Documents'
shpPath = fr'{homeDir}\Qplus\shp\客製化單位\{agency_name}\{shpName}.shp'    # TWD67-LatLong
outPath = fr'{homeDir}\Qplus\tab\{agency_name}warning_list.csv'

shpData = gpd.read_file(shpPath , encoding = 'utf-8').sort_values(by = sort_name , ignore_index = True)
gs = gpd.GeoSeries(shpData.geometry[:] , crs = 'EPSG:3821')
num_area = len(gs)

objectID = shpData['OBJECTID_1']
district = shpData['行政區']
threshold = shpData['淹水值']
idx_in_district = shpData['編號1']
ref_station = shpData['參考站']

stid_num = 0
idxGrid_in_district = 0
district_cmp = []
idx_in_district_cmp = []
item_num = []
num_code = []
institution = []
section_name = []
stid = []
stname = []
qpegc = []
qpf = []
for cnt_area in np.arange(0 , num_area):
    idxGrid_in_district += 1
    if district[cnt_area] != district_cmp:
        idxGrid_in_district = 1
    if idx_in_district[cnt_area] != idx_in_district_cmp or district[cnt_area] != district_cmp:
        idx_in_district_cmp = idx_in_district[cnt_area]
        district_cmp = district[cnt_area]
        stid_num += 1
    item_num.append(f'{stid_num:03d}')
    num_code.append(f'{idxGrid_in_district:03d}')
    institution.append(district[cnt_area])
    section_name.append(f'{district[cnt_area]}({idx_in_district[cnt_area]})')
    stid.append(f'{agency_name}{stid_num:03d}')
    stname.append(section_name[cnt_area])
    qpegc.append(f'{threshold[cnt_area]:.2f}')
    qpf.append(f'{threshold[cnt_area]:.2f}')

# shpData_out = {'District': district , 'Threshold': threshold , 'Index in District': idx_in_district , 'Ref. Station': ref_station , 'geometry': gs}
# gdf = gpd.GeoDataFrame(shpData_out , crs = 'EPSG:3821')

with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
    writer = csv.writer(fo)
    writer.writerow(['item_num' , 'num_code' , 'institution' , 'section_name' , 'stid' , 'stname' , 'qpegc' , 'qpf' , 'alarm_level'])
    for cnt_area in np.arange(0 , num_area):
        writer.writerow([item_num[cnt_area] , num_code[cnt_area] , institution[cnt_area] , section_name[cnt_area] , stid[cnt_area] , stname[cnt_area] , qpegc[cnt_area] , 'NULL' , 'WARNING'])
        writer.writerow([item_num[cnt_area] , num_code[cnt_area] , institution[cnt_area] , section_name[cnt_area] , stid[cnt_area] , stname[cnt_area] , 'NULL' , qpf[cnt_area] , 'WARNING'])

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
idx_table[:] = np.nan

# with open(outPath , 'w' , newline = '' , encoding = 'utf-8') as fo:
#     writer = csv.writer(fo)
#     writer.writerow(['Index of Grid' , 'District' , 'Threshold' , 'Index Grid in Shape' , 'Ref. Station' , 'Extended Range' , 'Index of X' , 'Index of Y'])
#     for cnt_area in np.arange(0 , num_area):
#         for cnt_y in np.arange(0 , num_y):
#             for cnt_x in np.arange(0 , num_x):
#                 if np.isnan(idx_table[cnt_x , cnt_y]) & gs[cnt_area].contains(gm.Point((Lon[cnt_x , cnt_y] , Lat[cnt_x , cnt_y]))):
#                     idx_table[cnt_x , cnt_y] = cnt_area + 1
#                     writer.writerow([int(idx_table[cnt_x , cnt_y]) , district[cnt_area] , threshold[cnt_area] , idx_grid_in_shape[cnt_area] , ref_station[cnt_area] , 0 , cnt_x + 1 , cnt_y + 1])
#                     break
#             else:
#                 continue
#             break
#         else:
#             continue
#         break
