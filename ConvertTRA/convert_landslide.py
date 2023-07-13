import csv
import numpy as np
import pandas as pd
from pathlib import Path

inPath = Path(r'C:\Users\wjchen\Documents\QPEplus\ConvertTRA\raw\台鐵局土石流潛勢溪流_20221214.csv')
outPath = Path(r'C:\Users\wjchen\Documents\QPEplus\ConvertTRA\output\TRA_mudslide_20221214.csv')

df = pd.read_csv(inPath , encoding = 'utf-8')
df = df[['項次' , '工務段及分駐所' , '路段' , '編號' , '行政區' , '溪流名稱']]
df.columns = ['item_num' , 'institution' , 'section_name1' , 'section_name2' , 'section_name3' , 'section_name4']

for i , item_num in enumerate(df['item_num']):
    if np.isnan(item_num):
        idx_drop = i
        break

df.drop(range(idx_drop , df.shape[0]) , axis = 0 , inplace = True)
df = df.astype({'item_num': 'int'})
# df = df.astype({'item_num': 'str'})
# for i , item_num in enumerate(df['item_num']):
#     df['item_num'][i] = item_num.zfill(3)

df.to_csv(outPath , index = False)