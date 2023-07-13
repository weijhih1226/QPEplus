import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader as shprd
from cartopy.feature import ShapelyFeature as shpft

shpPath = r'C:\Users\wjchen\Documents\QPEplus\shp\taiwan_county\COUNTY_MOI_1090820.shp'
shp = shpft(shprd(shpPath).geometries() , ccrs.PlateCarree() , 
            facecolor = (1 , 1 , 1 , 0) , edgecolor = (0 , 0 , 0 , 1) , linewidth = 1 , zorder = 10)
print(list(shprd(shpPath).geometries()))