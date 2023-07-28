########################################
############# plot_RWRF.py #############
######### Author: Wei-Jhih Chen ########
########## Update: 2023/06/17 ##########
########################################

from cmath import log10
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime as dtdt
from pathlib import Path
from matplotlib.colors import ListedColormap , BoundaryNorm
from cartopy.io.shapereader import Reader as shprd
from cartopy.feature import ShapelyFeature as shpft
from color.color import read_colors

C2K = 273.15
DIM_X = 450
DIM_X_G = 451
DIM_Y = 450
DIM_Y_G = 451
DIM_Z = 51
DIM_Z_G = 52
DIM_S_G = 4

FREQ = 5.5027 * 1e9     # Units: Hz
V_LGHT = 2.997925 * 1e8 # Units: m s-1
SIGMA1 = 12.5664e8

CASE_DATETIME = dtdt(2023 , 5 , 31 , 0 , 0 , 0)
DATETIME_STR = CASE_DATETIME.strftime('%Y/%m/%d %H:%MZ')
PRODUCTS = {## Grid
            # 'XLAT': {'dname': 'Latitude' , 'units': '$^o$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'XLONG': {'dname': 'Longitude' , 'units': '$^o$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'F': {'dname': 'Coriolis Sine Latitude Term' , 'units': 's$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'HGT': {'dname': 'Terrain Height' , 'units': 'km' , 'offset': (0 , 1000) , 'shape': (DIM_Y , DIM_X)} , 
            ## Ground
            # 'PSFC': {'dname': 'Psfc' , 'units': 'hPa' , 'offset': (0 , 100) , 'shape': (DIM_Y , DIM_X)} , 
            # 'U10': {'dname': 'U at 10m' , 'units': 'm s$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'V10': {'dname': 'V at 10m' , 'units': 'm s$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'Q2': {'dname': 'QV at 2m' , 'units': 'kg kg$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'T2': {'dname': 'Temp. at 2m' , 'units': '$^{o}C$' , 'offset': (C2K , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'TH2': {'dname': 'Pot. Temp. at 2m' , 'units': 'K' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'LU_INDEX': {'dname': 'Land Use Category' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'VAR_SSO': {'dname': 'Variance of Subgrid-scale Orography' , 'units': 'm$^{2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'NEST_POS': {'dname': 'NEST_POS' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SEAICE': {'dname': 'Sea Ice Flag' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'XICEM': {'dname': 'Sea Ice Flag (Previous Step)' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'IVGTYP': {'dname': 'Dominant Vegetation Category' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'ISLTYP': {'dname': 'Dominant Soil Category' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'VEGFRA': {'dname': 'Vegetation Fraction' , 'units': '%' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'CANWAT': {'dname': 'Canopy Water' , 'units': 'kg m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'LAI': {'dname': 'Leaf Area Index' , 'units': 'm$^{-2}$/m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'VAR': {'dname': 'Orographic Variance' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'RAINC': {'dname': 'Accumulated Total Cumulus Precipitation' , 'units': 'mm' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'RAINSH': {'dname': 'Accumulated Shallow Cumulus Precipitation' , 'units': 'mm' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'RAINNC': {'dname': 'Accumulated Total Grid Scale Precipitation' , 'units': 'mm' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SNOW': {'dname': 'Snow Water Equivalent' , 'units': 'kg m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SNOWH': {'dname': 'Physical Snow Depth' , 'units': 'km' , 'offset': (0 , 1000) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SNOWC': {'dname': 'Flag Indicating Snow Coverage (1: Snow Cover)' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SR': {'dname': 'Fraction of Frozen Precipitation' , 'units': '%' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SST': {'dname': 'Sea Surface Temperature' , 'units': 'K' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SSTSK': {'dname': 'Skin Sea Surface Temperature' , 'units': 'K' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'TSK': {'dname': 'Surface Skin Temperature' , 'units': '$^{o}C$' , 'offset': (C2K , 1) , 'shape': (DIM_Y , DIM_X)} , 
            ## Column
            # 'UST': {'dname': 'U* in Similarity Theory' , 'units': 'm s$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'PBLH': {'dname': 'PBL Height' , 'units': 'km' , 'offset': (0 , 1000) , 'shape': (DIM_Y , DIM_X)} , 
            # 'MUB': {'dname': 'Base State Dry Air Mass in Column' , 'units': 'hPa' , 'offset': (0 , 100) , 'shape': (DIM_Y , DIM_X)} , 
            # 'MU': {'dname': 'Perturbation Dry Air Mass in Column' , 'units': 'hPa' , 'offset': (0 , 100) , 'shape': (DIM_Y , DIM_X)} , 
            ## Runoff
            # 'SFROFF': {'dname': 'Surface Runoff' , 'units': 'mm' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'UDROFF': {'dname': 'Underground Runoff' , 'units': 'mm' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            ## Mask
            # 'XLAND': {'dname': 'Land Mask (1: Land, 2: Water)' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'LANDMASK': {'dname': 'Land Mask (1: Land, 0: Water)' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            ## Flux
            # 'GRDFLX': {'dname': 'Ground Heat Flux' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'ACGRDFLX': {'dname': 'Accumulated Ground Heat Flux' , 'units': 'J m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'HFX': {'dname': 'Upward Heat Flux at the Surface' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'ACHFX': {'dname': 'Accumulated Upward Heat Flux at the Surface' , 'units': 'J m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'QFX': {'dname': 'Upward Moisture Flux at the Surface' , 'units': 'kg m$^{-2}$ s$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'LH': {'dname': 'Latent Heat Flux at the Surface' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'ACLHF': {'dname': 'Accumulated Upward Latent Heat Flux at the Surface' , 'units': 'J m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SWDOWN': {'dname': 'Downward Short Wave Flux at Ground Surface' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'SWNORM': {'dname': 'Normal Short Wave Flux at Ground Surface (Slope-dependent)' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'GSW': {'dname': 'Net Short Wave Flux at Ground Surface' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'GLW': {'dname': 'Downward Long Wave Flux at Ground Surface' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'OLR': {'dname': 'TOA Outgoing Long Wave' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'ALBEDO': {'dname': 'Albedo' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'ALBBCK': {'dname': 'Background Albedo' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'EMISS': {'dname': 'Surface Emissivity' , 'units': '' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            # 'NOAHRES': {'dname': 'Residual of the NOAH Surface Energy Budget' , 'units': 'W m$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            ## Upper Air
            # 'U': {'dname': 'X-wind Component' , 'units': 'm s$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X_G)} , 
            # 'V': {'dname': 'Y-wind Component' , 'units': 'm s$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y_G , DIM_X)} , 
            # 'W': {'dname': 'Z-wind Component' , 'units': 'cm s$^{-1}$' , 'offset': (0 , 100) , 'shape': (DIM_Z_G , DIM_Y , DIM_X)} , 
            # 'PH': {'dname': 'Perturbation Geopotential' , 'units': 'm$^{2}$ s$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Z_G , DIM_Y , DIM_X)} , 
            # 'PHB': {'dname': 'Base-state Geopotential' , 'units': 'm$^{2}$ s$^{-2}$' , 'offset': (0 , 1) , 'shape': (DIM_Z_G , DIM_Y , DIM_X)} , 
            # 'T': {'dname': 'Perturbation Pot. Temp.' , 'units': 'K' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'P': {'dname': 'Perturbation Pressure' , 'units': 'hPa' , 'offset': (0 , 100) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'PB': {'dname': 'Base-state Pressure' , 'units': 'hPa' , 'offset': (0 , 100) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'P_HYD': {'dname': 'Hydrostatic Pressure' , 'units': 'hPa' , 'offset': (0 , 100) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'QVAPOR': {'dname': 'Water Vapor Mixing Ratio' , 'units': 'kg kg$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'QCLOUD': {'dname': 'Cloud Water Mixing Ratio' , 'units': 'kg kg$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'QRAIN': {'dname': 'Rain Water Mixing Ratio' , 'units': 'kg kg$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'QICE': {'dname': 'Ice Mixing Ratio' , 'units': 'kg kg$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'QSNOW': {'dname': 'Snow Mixing Ratio' , 'units': 'kg kg$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'QGRAUP': {'dname': 'Graupel Mixing Ratio' , 'units': 'kg kg$^{-1}$' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            # 'CLDFRA': {'dname': 'Cloud Fraction' , 'units': '%' , 'offset': (0 , 1) , 'shape': (DIM_Z , DIM_Y , DIM_X)} , 
            ## Soil
            # 'TSLB': {'dname': 'Soil Temperature' , 'units': 'K' , 'offset': (0 , 1) , 'shape': (DIM_S_G , DIM_Y , DIM_X)} , 
            # 'SMOIS': {'dname': 'Soil Moisture' , 'units': 'm$^{3}$ m$^{-3}$' , 'offset': (0 , 1) , 'shape': (DIM_S_G , DIM_Y , DIM_X)} , 
            'SH2O': {'dname': 'Soil Liquid Water' , 'units': 'm$^{3}$ m$^{-3}$' , 'offset': (0 , 1) , 'shape': (DIM_S_G , DIM_Y , DIM_X)} , 
            'SMCREL': {'dname': 'Relative Soil Moisture' , 'units': '%' , 'offset': (0 , 0.01) , 'shape': (DIM_S_G , DIM_Y , DIM_X)} , 
            'TMN': {'dname': 'Soil Temperature at Lower Boundary' , 'units': 'K' , 'offset': (0 , 1) , 'shape': (DIM_Y , DIM_X)} , 
            }

HOME_DIR = Path(r'C:\Users\Showlong\Documents\QPEplus')
IN_DIR = HOME_DIR/'data'/'RWRF'
IN_FILE = f"wrfout_d01_{CASE_DATETIME.strftime('%Y-%m-%d_%H_%M_%S')}"
IN_PATH = IN_DIR/IN_FILE
OUT_DIR = HOME_DIR/'output'/'RWRF'

LON_DEG2KM = 102.8282
LAT_DEG2KM = 111.1361

CEN_LON = 120.813995
CEN_LAT = 23.7644

DX , DY = 2 , 2         # Units: km
NX , NY = 451 , 451
X_G = (np.arange(NX) - (NX - 1) / 2) * DX
Y_G = (np.arange(NY) - (NY - 1) / 2) * DY
LON_G = CEN_LON + X_G / LON_DEG2KM
LAT_G = CEN_LAT + Y_G / LAT_DEG2KM

X_MIN , X_MAX = np.min(LON_G) , np.max(LON_G)
Y_MIN , Y_MAX = np.min(LAT_G) , np.max(LAT_G)
X_TICKS = np.arange(X_MIN // 1 + 1 , X_MAX // 1 + 1)
Y_TICKS = np.arange(Y_MIN // 1 + 1 , Y_MAX // 1 + 1)

X_Ticklabel = []
Y_Ticklabel = []
for x_tick in X_TICKS:
    X_Ticklabel = np.append(X_Ticklabel , f'{x_tick}$^o$E')
for y_tick in Y_TICKS:
    Y_Ticklabel = np.append(Y_Ticklabel , f'{y_tick}$^o$N')

data = nc.Dataset(IN_PATH)
# vars = data.variables
# print(vars['T00'][0])
# print(data.DX)
DIM_X = data.dimensions['west_east'].size
DIM_X_G = data.dimensions['west_east_stag'].size
DIM_Y = data.dimensions['south_north'].size
DIM_Y_G = data.dimensions['south_north_stag'].size
DIM_Z = data.dimensions['bottom_top'].size
DIM_Z_G = data.dimensions['bottom_top_stag'].size

##### Map #####
shp_Coastline = 'C:/Users/Showlong/Documents/Tools/shp/natural_earth/physical/10m_coastline.shp'
shp_TWNcountyTWD97 = 'C:/Users/Showlong/Documents/Tools/shp/taiwan_county/COUNTY_MOI_1090820.shp'
shape_feature_Coastline = shpft(shprd(shp_Coastline).geometries(), ccrs.PlateCarree(),
                               linewidth = 1.0 , facecolor = (1. , 1. , 1. , 0.), 
                               edgecolor = 'w' , zorder = 10)
shape_feature_TWNcountyTWD97 = shpft(shprd(shp_TWNcountyTWD97).geometries(), ccrs.PlateCarree(),
                               linewidth = 0.2 , facecolor = (1. , 1. , 1. , 0.), 
                               edgecolor = (.3 , .3 , .3 , 1.) , zorder = 10)

LON_MG , LAT_MG = np.meshgrid(LON_G , LAT_G)
for product in PRODUCTS:
    var = (data.variables[product][0] - PRODUCTS[product]['offset'][0]) / PRODUCTS[product]['offset'][1]

    if len(var.shape) == 3:
        for cnt_z in range(var.shape[0]):
            OUT_PATH = OUT_DIR/f"{IN_FILE}_{product}_{cnt_z:02d}.png"
            plt.close()
            fig , ax = plt.subplots(figsize = (12 , 10) , subplot_kw = {'projection' : ccrs.PlateCarree()})
            fig.set_dpi(200)
            ax.text(0.125 , 0.905 , 'RWRF' , fontsize = 18 , ha = 'left' , color = '#666' , transform = fig.transFigure)
            ax.text(0.125 , 0.875 , PRODUCTS[product]['dname'] , fontsize = 20 , ha = 'left' , color = 'k' , transform = fig.transFigure)
            ax.text(0.744 , 0.905 , f'Layer {cnt_z:02d}' , fontsize = 18 , ha = 'right' , color = 'k' , transform = fig.transFigure)
            ax.text(0.744 , 0.875 , f'{DATETIME_STR} F00' , fontsize = 20 , ha = 'right' , color = 'k' , transform = fig.transFigure)
            ax.set_extent([X_MIN , X_MAX , Y_MIN , Y_MAX])
            ax.gridlines(xlocs = X_TICKS , ylocs = Y_TICKS , color = '#bbb' , linewidth = 0.5 , alpha = 0.5 , draw_labels = False)
            pc = ax.pcolormesh(LON_MG , LAT_MG , var[cnt_z] , shading = 'flat' , cmap = 'jet')
            ax.add_feature(shape_feature_TWNcountyTWD97)
            ax.add_feature(shape_feature_Coastline)
            plt.xticks(X_TICKS , X_Ticklabel , size = 10)
            plt.yticks(Y_TICKS , Y_Ticklabel , size = 10)
            cbar = plt.colorbar(pc)
            cbar.set_label(PRODUCTS[product]['units'] , size = 12)
            fig.savefig(OUT_PATH)

    else:
        OUT_PATH = OUT_DIR/f"{IN_FILE}_{product}.png"
        plt.close()
        fig , ax = plt.subplots(figsize = (12 , 10) , subplot_kw = {'projection' : ccrs.PlateCarree()})
        fig.set_dpi(200)
        ax.text(0.125 , 0.905 , 'RWRF' , fontsize = 18 , ha = 'left' , color = '#666' , transform = fig.transFigure)
        ax.text(0.125 , 0.875 , PRODUCTS[product]['dname'] , fontsize = 20 , ha = 'left' , color = 'k' , transform = fig.transFigure)
        ax.text(0.744 , 0.905 , f'{DATETIME_STR}' , fontsize = 20 , ha = 'right' , color = 'k' , transform = fig.transFigure)
        ax.text(0.744 , 0.875 , 'F00' , fontsize = 20 , ha = 'right' , color = 'k' , transform = fig.transFigure)
        ax.set_extent([X_MIN , X_MAX , Y_MIN , Y_MAX])
        ax.gridlines(xlocs = X_TICKS , ylocs = Y_TICKS , color = '#bbb' , linewidth = 0.5 , alpha = 0.5 , draw_labels = False)
        pc = ax.pcolormesh(LON_MG , LAT_MG , var , shading = 'flat' , cmap = 'jet')
        ax.add_feature(shape_feature_TWNcountyTWD97)
        ax.add_feature(shape_feature_Coastline)
        plt.xticks(X_TICKS , X_Ticklabel , size = 10)
        plt.yticks(Y_TICKS , Y_Ticklabel , size = 10)
        cbar = plt.colorbar(pc)
        cbar.set_label(PRODUCTS[product]['units'] , size = 12)
        fig.savefig(OUT_PATH)

# qvapor = (data.variables['QVAPOR'][0] - PRODUCTS['QVAPOR']['offset'][0]) / PRODUCTS['QVAPOR']['offset'][1]
# qrain = (data.variables['QRAIN'][0] - PRODUCTS['QRAIN']['offset'][0]) / PRODUCTS['QRAIN']['offset'][1]
# qsnow = (data.variables['QSNOW'][0] - PRODUCTS['QSNOW']['offset'][0]) / PRODUCTS['QSNOW']['offset'][1]
# qgraup = (data.variables['QGRAUP'][0] - PRODUCTS['QGRAUP']['offset'][0]) / PRODUCTS['QGRAUP']['offset'][1]

# Rd = 287.05
# Rv = 461.5
# p = data.variables['PB'][0] + data.variables['P'][0]
# theta = data.variables['T00'][0] + data.variables['T'][0]
# theta_v = theta * (1 + 0.61 * qvapor)
# rho_moist = p / (Rd * theta_v)

def lfm_reflectivity(lx , ly , nz , rho , hgt , rainmr , icemr , snowmr , graupelmr , 
                     refl , zdr , ldr , tmp , p , qv , max_refl , echo_tops):
    svnfrth = 7 / 4
    max_top_thresh = 5
    c_m2z = 'rams'

    max_refl = np.zeros((lx , ly))
    echo_tops = 1e37
    if c_m2z != 'wrf':
        refl = 0
    else:
        refl = max(refl , -10)
        refl[refl < 0 and refl > -10] = 0

    zdr = 0
    ldr = 0
    print(f'c_m2z = {c_m2z}')

    if c_m2z == 'rip':
        in0r = 0
        in0s = 0
        in0g = 0
        iliqskin = 0

        for j in range(ly):
            for i in range(lx):
                max_refl[i , j] = np.max(refl[i , j , :])

    else:
        for j in range(ly):
            for i in range(lx):
                for k in range(nz):
                    if c_m2z == 'rams':
                        w = 264083.11 * (rainmr[i , j , k] + 0.2 * snowmr[i , j , k] + 2 * graupelmr[i , j , k])
                        w = max(w , 1)
                        refl[i , j , k] = 17.8 * np.log10(w)
                        if refl[i , j , k] == 0:
                            refl[i , j , k] = -10

                    elif c_m2z == 'kessler':
                        refl[i , j , k] = (17300 * rho[i , j , k] * 1000 * max(rainmr[i , j , k] , 0)) ** svnfrth
                        # Add the ice component
                        refl[i , j , k] += 38000 * (rho[i , j , k] * 1000 * 
                                                    # max(icemr[i , j , k] + snowmr[i , j , k] + graupelmr[i , j , k] , 0)) ** 2.2
                                                    max(snowmr[i , j , k] + graupelmr[i , j , k] , 0)) ** 2.2
                        refl[i , j , k] = 10 * np.log10(max(refl[i , j , k] , 1))
                        if refl[i , j , k] == 0:
                            refl[i , j , k] = -10

                    elif c_m2z == 'synp':
                        # versuch(rainmr[i , j , k] , snowmr[i , j , k] , graupelmr[i , j , k] , tmp[i , j , k] , 
                        # zhhx[i , j , k] , ahhx[i , j , k] , zhvx[i , j , k] , zvhx[i , j , k] , zvvx[i , j , k] , 
                        # p[i , j , k] , qv[i , j , k] , delahvx[i , j , k] , kkdp[i , j , k] , rhohvx[i , j , k])
                        # zvvxmax = max(zvvx[i , j , k] , 1)
                        # zhhxmax = max(zhhx[i , j , k] , 1)
                        # refl[i , j , k] = 10 * np.log10(zhhxmax)
                        # zdr[i , j , k] = 10 * np.log10(zhhx[i , j , k]/zvvxmax)
                        # ldr[i , j , k] = 10 * np.log10(zvhx[i , j , k]/zhhxmax)
                        pass
                        
                    if refl[i , j , k] >= max_top_thresh:
                        echo_tops[i , j] = hgt[i , j , k]

                max_refl[i , j] = np.max(refl[i , j , :])

    rainmr *= rho
    snowmr *= rho
    # icemr *= rho
    graupelmr *= rho

    return

def reflectivity_kessler(rho , rainmr , snowmr , graupelmr):
    svnfrth = 7 / 4
    rainmr[rainmr < 0] = 0
    refl = (17300 * rho * rainmr) ** svnfrth
    # icetotalmr = icemr + snowmr + graupelmr
    icetotalmr = snowmr + graupelmr
    icetotalmr[icetotalmr < 0] = 0
    refl += 38000 * (rho * icetotalmr) ** 2.2
    refl[refl < 1] = 1
    refl = 10 * np.log10(refl)
    refl[refl == 0] = -10
    return refl

def reflectivity_rams(rainmr , snowmr , graupelmr):
    refl = 264083.11 * (rainmr + 0.2 * snowmr + 2 * graupelmr)
    refl[refl < 1] = 1
    refl = 17.8 * np.log10(refl)
    refl[refl == 0] = -10
    return refl

def watereps(temp):
    # -----------------------------------------------------------------------
    #     This routine calculates the complex relative dielectric constant
    #     of liquid and ice phase water using an empirical model developed
    #     by P. S. Ray, 1972, Applied Optics, 11(8):1836-1844
    #     Applicable range: wvln: 1 to 600 mm;  freq: 0.5 to 300 GHz
    #     Temperarure (Celsius degree):  ice: -20 to 0, water: -20 to 50
    #     exp(+jwt) convention
    # -----------------------------------------------------------------------
    WVLN = 1000 * V_LGHT / FREQ         # Units: mm
    WVLN_UM = 1e6 * V_LGHT / FREQ       # Units: microns

    # ***********************************************************************
    # Berechnung der dielectrischen Konstanten f�r Wasser      
    # ***********************************************************************
    einf1 = 5.27137 + (0.0216474 - 0.131198e-2 * temp) * temp       # (7a)
    alpha1 = -16.8129 / (temp + C2K) + 0.609265e-1                # (7b)
    tt = temp - 25.0
    estamf1 = 78.54 * (1 - 4.579e-3 * tt + 1.19e-5 * tt * tt - 2.8e-8 * tt ** 3) - einf1
    xx1 = ((0.33836e-2 * np.exp(2513.98 / (temp + C2K))) / WVLN) ** (1 - alpha1)
    yy1 = 1 + 2 * xx1 * np.sin(alpha1 * np.pi / 2) + xx1 * xx1
    epswtr = complex(estamf1 * (1 + xx1 * np.sin(alpha1 * np.pi / 2)) / yy1 + einf1 , -estamf1 * xx1 * np.cos(alpha1 * np.pi / 2) / yy1 + SIGMA1 * WVLN / 18.8496e10)
    
    # **************************************************************************
    # Berechnung der dielectrischen Konstanten f�r Eis
    # **************************************************************************
    tempx = temp
    if (temp > -1): tempx = -1.5
    T_grid = np.zeros(4)
    lam_grid = np.zeros(21)
    ri = np.zeros((4 , 21) , dtype = complex)
    ri_real = np.zeros(2)
    ri_im = np.zeros(2)

    # interpoliere in T & lam
    for i in range(3):
        if (tempx < T_grid[i] and tempx >= T_grid[i + 1]):
            for k in range(2):
                kk = i + k - 1
                for j in range(20):
                    if (WVLN_UM >= lam_grid[j] and WVLN_UM < lam_grid[j + 1]):
                        lam_low = lam_grid[j]
                        lam_high = lam_grid[j + 1]
                        m_real = (ri[kk , j + 1].real - ri[kk , j].real) / (np.log(lam_high) - np.log(lam_low))
                        b_real = ri[kk , j].real - m_real * np.log(lam_low)
                        m_im = (ri[kk , j + 1].imag - ri[kk , j].imag) / (np.log(lam_high) - np.log(lam_low))
                        b_im = ri[kk , j].imag - m_im * np.log(lam_low)
                        ri_real[k] = m_real * np.log(WVLN_UM) + b_real
                        ri_im[k] = m_im * np.log(WVLN_UM) + b_im
            T_low = T_grid[i + 1]
            T_high = T_grid[i]
            m_real = (ri_real[0] - ri_real[1]) / (T_high - T_low)
            b_real = ri_real[1] - m_real * T_low
            m_im = (ri_im[0] - ri_im[1]) / (T_high-T_low)
            b_im = ri_im[1] - m_im * T_low
            ri_real_final = m_real * tempx + b_real
            ri_im_final = m_im * tempx + b_im

    testre =  ri_real_final ** 2 -  ri_im_final ** 2
    testim = 2 * ri_real_final * ri_im_final
    epsice = complex(testre , testim)

    return epswtr , epsice

# def reflectivity_synp(rainmr , snowmr , graupelmr , tmp , p , qv):
#     thrdr = np.zeros(2)
#     tmp -= C2K
#     zhhx = 0
#     thrdr[1] = 0    # radar elevation angle, 0=horizontal
#     nrank = 0

#     # refractive index of air
#     refreair = 1
#     refimair = 0

#     NDR = 1         # Number of Radar looking directions
#     WVLN = V_LGHT / FREQ

#     # Set drop size distribution (DSD) for each category
#     sznum = 0
#     szlow = 0
#     szupp = 0
#     sdidv = 0
#     sdgno = 0
#     sdgmm = 0
#     sdgml = 0
#     lambd = 0

#     # Select the model hydrometeors types in the cloud, in the order of:
#     # cldrp(cloud droplet),rains(rain drop),icclm(pristine ice column),
#     # icplt(pristine ice plate),snows(snow flake),aggrs(aggregate),
#     # graup(graupel),hlcnc(conical hail),hlsph(spheroidal hail).
#     # e.g., hyddo='010000100' means to consider rain and graupel only.

#     hyddo = '000000000'
#     if (rainmr > 0.): hyddo[1] = '1'
#     if (snowmr > 0.): hyddo[3] = '1'
#     if (graupelmr > 0.): hyddo[6] = '1'

#     tv = (tmp + C2K) * (1 + 0.61 * qv)       # virtuelle Temperatur
#     rhox = p / (287 * tv)                       # Luftdichte �ber Gasgleichung

#     return zhhx , ahhx , zhvx , zvhx , zvvx , delahvx , kkdp , rhohvx


colors = read_colors('dbz_65')
lvls = np.arange(0 , 67)
cmap = ListedColormap(colors)
norm = BoundaryNorm(lvls , cmap.N)

# refl = reflectivity_rams(qrain , qsnow , qgraup)
# # refl = reflectivity_kessler(rho_moist , qrain , qsnow , qgraup)
# refl[refl == -10] = np.nan

# max_refl = np.nanmax(refl , axis = 0)

# for cnt_z in range(refl.shape[0]):
#     OUT_PATH = OUT_DIR/f"{IN_FILE}_REFL_{cnt_z:02d}.png"
#     plt.close()
#     fig , ax = plt.subplots(figsize = (12 , 10) , subplot_kw = {'projection' : ccrs.PlateCarree()})
#     fig.set_dpi(200)
#     ax.text(0.125 , 0.905 , 'RWRF' , fontsize = 18 , ha = 'left' , color = '#666' , transform = fig.transFigure)
#     ax.text(0.125 , 0.875 , 'Reflectivity' , fontsize = 20 , ha = 'left' , color = 'k' , transform = fig.transFigure)
#     ax.text(0.744 , 0.905 , f'Layer {cnt_z:02d}' , fontsize = 18 , ha = 'right' , color = 'k' , transform = fig.transFigure)
#     ax.text(0.744 , 0.875 , f'{DATETIME_STR} F00' , fontsize = 20 , ha = 'right' , color = 'k' , transform = fig.transFigure)
#     ax.set_extent([X_MIN , X_MAX , Y_MIN , Y_MAX])
#     ax.gridlines(xlocs = X_TICKS , ylocs = Y_TICKS , color = '#bbb' , linewidth = 0.5 , alpha = 0.5 , draw_labels = False)
#     pc = ax.pcolormesh(LON_MG , LAT_MG , refl[cnt_z] , shading = 'flat' , cmap = cmap , norm = norm)
#     pc.set_clim(min(lvls) , max(lvls))
#     ax.add_feature(shape_feature_TWNcountyTWD97)
#     ax.add_feature(shape_feature_Coastline)
#     plt.xticks(X_TICKS , X_Ticklabel , size = 10)
#     plt.yticks(Y_TICKS , Y_Ticklabel , size = 10)
#     cbar = plt.colorbar(pc , ticks = range(0 , 70 , 5))
#     cbar.set_label('dBZ' , size = 12)
#     fig.savefig(OUT_PATH)

# OUT_PATH = OUT_DIR/f"{IN_FILE}_REFL_CV2.png"
# plt.close()
# fig , ax = plt.subplots(figsize = (12 , 10) , subplot_kw = {'projection' : ccrs.PlateCarree()})
# fig.set_dpi(200)
# ax.text(0.125 , 0.905 , 'RWRF' , fontsize = 18 , ha = 'left' , color = '#666' , transform = fig.transFigure)
# ax.text(0.125 , 0.875 , 'Reflectivity' , fontsize = 20 , ha = 'left' , color = 'k' , transform = fig.transFigure)
# ax.text(0.744 , 0.905 , 'CV' , fontsize = 18 , ha = 'right' , color = 'k' , transform = fig.transFigure)
# ax.text(0.744 , 0.875 , f'{DATETIME_STR} F00' , fontsize = 20 , ha = 'right' , color = 'k' , transform = fig.transFigure)
# ax.set_extent([X_MIN , X_MAX , Y_MIN , Y_MAX])
# ax.gridlines(xlocs = X_TICKS , ylocs = Y_TICKS , color = '#bbb' , linewidth = 0.5 , alpha = 0.5 , draw_labels = False)
# pc = ax.pcolormesh(LON_MG , LAT_MG , max_refl , shading = 'flat' , cmap = cmap , norm = norm)
# pc.set_clim(min(lvls) , max(lvls))
# ax.add_feature(shape_feature_TWNcountyTWD97)
# ax.add_feature(shape_feature_Coastline)
# plt.xticks(X_TICKS , X_Ticklabel , size = 10)
# plt.yticks(Y_TICKS , Y_Ticklabel , size = 10)
# cbar = plt.colorbar(pc , ticks = range(0 , 70 , 5))
# cbar.set_label('dBZ' , size = 12)
# fig.savefig(OUT_PATH)