import json
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime as dtdt

month = 11

# product = '一級監控路段雨量'
# product_code = 2
# num_item = 30
# product = '一級監控橋梁雨量'
# product_code = 3
# num_item = 11
product = '二級監控路段雨量'
product_code = 4
num_item = 29

homeDir = Path(r'C:\Users\wjchen\Documents\QPEplus')
inDir = homeDir/'data'/'sectiondisplay_file'/'THB'/'2022'/f'{month:02d}'
inPaths = list(inDir.glob(f'{str(product_code)}_*.json'))
outPath = homeDir/'WarningLight'/f'warning_light_statics_{product}_{month:02d}月.csv'

items = [f'{i + 1:03d}' for i in range(num_item)]

count = {}
count['Datetime'] = []
for item in items:
    count[item] = []

for path in tqdm(inPaths):
    datetime = dtdt.strptime(str(path)[-17:-5] , '%Y%m%d%H%M')

    with open(path , 'r' , encoding = 'UTF-8') as f:
        data = json.load(f)
        summary_table = data['summary-table'][product]
        if summary_table:
            # FLIP WARN CODE
            for item in items:
                if summary_table[item] == 1:
                    summary_table[item] = 3
                elif summary_table[item] == 3:
                    summary_table[item] = 1

            # RECALCULATE WARN CODE
            for f in data['features']:
                item_num = f['properties']['項次']
                warn_text = f['properties']['警示']
                if warn_text == '行動':
                    warn_code = 3
                elif warn_text == '警戒':
                    warn_code = 2
                elif warn_text == '預警':
                    warn_code = 1
                else:
                    warn_code = 0
                if warn_code > summary_table[item_num]:
                    summary_table[item_num] = warn_code

            # COUNT WANN CODE
            cnt_0 = cnt_1 = cnt_2 = cnt_3 = 0
            for item in items:
                if summary_table[item] == 1:
                    cnt_1 += 1
                elif summary_table[item] == 2:
                    cnt_2 += 1
                elif summary_table[item] == 3:
                    cnt_3 += 1
                else:
                    cnt_0 += 1
            
            # APPEND CASE
            if cnt_1 + cnt_2 + cnt_3 != 0:
                count['Datetime'].append(datetime)
                for item in items:
                    count[item].append(summary_table[item])

count = pd.DataFrame(count)
count.to_csv(outPath , index = False)