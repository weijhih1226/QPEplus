########################################
########### merge_geojson.py ###########
######## Author: Wei-Jhih Chen #########
########## Update: 2023/03/29 ##########
########################################

import json
from pathlib import Path

NAME_GEOJSON = '112_大規模崩塌潛勢區_20230324'
NAME1 = '112_大規模崩塌第一類_20230324'
NAME2 = '112_大規模崩塌第二類_20230324'

HOMEDIR = Path(r'C:\Users\wjchen\Documents\QPEplus')
INDIR = HOMEDIR/'geojson'/'Agency'/'SWCB_collapse'
INPATH1 = INDIR/'112_大規模崩塌影響範圍_20230324.geojson'
INPATH2 = INDIR/'112_大規模崩塌警戒發布區_20230324.geojson'
OUTPATH = INDIR/f'{NAME_GEOJSON}.geojson'
OUTPATH1 = INDIR/f'{NAME1}.geojson'
OUTPATH2 = INDIR/f'{NAME2}.geojson'

def filter_type(data):
    cnt = 0
    while cnt < len(data['features']):
        if data['features'][cnt]['properties']['Warn_type'] == 1 or data['features'][cnt]['properties']['Warn_type'] is None:
            data['features'].pop(cnt)
            cnt -= 1
        cnt += 1
    return data


def main():
    with open(INPATH1 , encoding = 'UTF-8') as f:
        data1 = json.load(f)

    with open(INPATH2 , encoding = 'UTF-8') as f:
        data2 = json.load(f)

    crs1 = data1['crs']['properties']['name']
    crs2 = data2['crs']['properties']['name']

    if crs1 == crs2:
        data1['name'] = NAME_GEOJSON
        for feature in data2['features']:
            data1['features'].append(feature)

    # data1 = filter_type(data1)

    with open(OUTPATH , 'w' , encoding = 'UTF-8' , newline = '') as f:
        json.dump(data1 , f)

if __name__ == '__main__':
   main()