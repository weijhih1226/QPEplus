# -*- coding: utf-8 -*-

import numpy as np
import geopandas as gpd
from shapely import geometry as gm

df1 = gpd.read_file(r'C:\Users\wjchen\Documents\QPEplus\Test\geojson\MARK_捷運車站_1111103.geojson')
df2 = gpd.read_file(r'C:\Users\wjchen\Documents\QPEplus\Test\geojson\MARK_捷運車站_1111103_10m.geojson')

gm1 = df1.geometry
gm2 = df2.geometry
gm0 = gm1.append(gm2)

x , y = np.array(gm2[1].geoms[0].exterior.coords.xy)

print(x , y)

# gm0.to_file(r'C:\Users\wjchen\Documents\QPEplus\Test\geojson\MARK_捷運車站_1111103_merge.geojson' , driver = "GeoJSON")