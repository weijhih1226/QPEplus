########################################
############ plot_radar.py #############
######## Author: Wei-Jhih Chen #########
########## Update: 2022/10/26 ##########
########################################

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from shapely import geometry as gm
from matplotlib.colors import ListedColormap , BoundaryNorm
from cartopy.io.shapereader import Reader as shprd
from cartopy.feature import ShapelyFeature as shpft

def main():
    pass
    # Plot
    # shpTWNPath = homeDir/'shp'/'TWD67'/'taiwan_county'/'COUNTY_MOI_1090820_TWD67.shp'
    # shpTWN = shpft(shprd(shpTWNPath).geometries() , ccrs.PlateCarree() , 
    #                facecolor = (1 , 1 , 1 , 0) , edgecolor = (0 , 0 , 0 , 1) , linewidth = 1)
    # colors = ['#c1c1c1' , '#99ffff' , '#00ccff' , '#0099ff' , '#0066ff' , '#339900' , '#33ff00' , '#ffff00' , '#ffcc00' , '#ff9900' , 
    #           '#ff0000' , '#cc0000' , '#a50000' , '#990099' , '#cc00cc' , '#ff00ff' , '#ffccff']
    # levels = [0.1 , 1 , 2 , 6 , 10 , 15 , 20 , 30 , 40 , 50 , 70 , 90 , 110 , 130 , 150 , 200 , 300 , 500]
    # ticks = [0.1 , 1 , 2 , 6 , 10 , 15 , 20 , 30 , 40 , 50 , 70 , 90 , 110 , 130 , 150 , 200 , 300]
    # tickLabels = ticks
    # varUnits = 'mm hr$^{-1}$'
    # cmin = 0.1
    # cmax = 500
    # data[data < cmin] = np.nan
    # data[data > cmax] = cmax

    # cmap = ListedColormap(colors)
    # norm = BoundaryNorm(levels , cmap.N)
    # plt.close()
    # fig , ax = plt.subplots(figsize = [12 , 10] , subplot_kw = {'projection' : ccrs.PlateCarree()})
    # ax.add_feature(shpTWN , zorder = 2)
    # PC = ax.pcolormesh(LonG , LatG , data , shading = 'flat' , cmap = cmap , norm = norm , alpha = 1 , zorder = 1)
    # # ax.scatter(Lon[idxX , idxY] , Lat[idxX , idxY] , 5 , zorder = 3)
    # gs.boundary.plot(ax = ax , color = 'k' , linewidth = 0.2 , zorder = 4)
    # # ax.axis([lon_start , lon_end , lat_start , lat_end])
    # ax.set_xticks(np.arange(lonStart * 10 , lonEnd * 10 , 5) / 10)
    # ax.set_yticks(np.arange(latStart * 10 , latEnd * 10 , 5) / 10)
    # ax.axis([120 , 122 , 22 , 25])
    # cbar = plt.colorbar(PC , orientation = 'vertical' , ticks = ticks)
    # cbar.ax.set_yticklabels(tickLabels)
    # cbar.ax.tick_params(labelsize = 12)
    # cbar.set_label(varUnits , rotation = 0 , labelpad = -20 , y = 1.03 , size = 12)
    # plt.show()

if __name__ == '__main__':
    main()