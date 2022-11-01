########################################
############ read_radar.py #############
######## Author: Wei-Jhih Chen #########
########## Update: 2022/10/27 ##########
########################################

import gzip , struct
import numpy as np

HEADER_LENGTH = 20  # HEADER_LENGTH = 1 -> b'\x00\x00\x00\x00' -> (16 * 2) ** 4 -> 256 ** 4 -> 4_294_967_296
BYTE_ORDER = '<'    # little-endian (<)

class readMosaic2D:

    '''
    1. If fPath is a .gz file then gunzip the file first, 
       or directly open the binary file.
    2. Default is to get the header and other information 
       (the time of the observation; mapping information; 
       layer numbers, scale; mosaic radar numbers & names; 
       the name, units, scale, missing value of the variable).
    3. Use getData() after instantiating the class to get 
       data values of each grid.
    '''

    def __init__(self , fPath):
        self.__byte = gunzipAndReadByte(fPath)
        self.getHeader()
        self.getInfo()

    def getHeader(self):
        header = []
        for cnt_para in range(HEADER_LENGTH):
            cnt_byte = cnt_para * 4
            if cnt_para != 9: header.append(struct.unpack(f'{BYTE_ORDER}L' , self.__byte[cnt_byte : cnt_byte + 4])[0])
            else: header.append(struct.unpack('2s' , self.__byte[39 : 37 : -1])[0].decode())

        self.__Year = header[0]
        self.__Month = header[1]
        self.__Day = header[2]
        self.__Hour = header[3]
        self.__Minute = header[4]
        self.__Second = header[5]
        
        self.__xNum = header[6]
        self.__yNum = header[7]
        self.__zNum = header[8]

        mapScale = header[10]

        aLonLatScale = header[16]
        self.__aLon = header[14] / aLonLatScale
        self.__aLat = header[15] / aLonLatScale

        dxyScale = header[19]
        self.__dx = header[17] / dxyScale
        self.__dy = header[18] / dxyScale
        
        return {'Year': self.__Year , 'Month': self.__Month , 'Day': self.__Day , 
                'Hour': self.__Hour , 'Minute': self.__Minute , 'Second': self.__Second , 
                'xNum': self.__xNum , 'yNum': self.__yNum , 'zNum': self.__zNum , 
                'aLon': self.__aLon , 'aLat': self.__aLat , 'dx': self.__dx , 'dy': self.__dy}

    def getYear(self):
        return self.__Year

    def getMonth(self):
        return self.__Month

    def getDay(self):
        return self.__Day

    def getHour(self):
        return self.__Hour

    def getMinute(self):
        return self.__Minute

    def getSecond(self):
        return self.__Second

    def getXNum(self):
        return self.__xNum

    def getYNum(self):
        return self.__yNum

    def getZNum(self):
        return self.__zNum

    def getALon(self):
        return self.__aLon

    def getALat(self):
        return self.__aLat

    def getDx(self):
        return self.__dx

    def getDy(self):
        return self.__dy

    def getZInfo(self):
        self.__zHt = np.zeros(self.__zNum , dtype = int)
        for cnt_para in range(HEADER_LENGTH , HEADER_LENGTH + self.__zNum):
            cnt_byte = cnt_para * 4
            self.__zht[cnt_para - HEADER_LENGTH] = struct.unpack(f'{BYTE_ORDER}L' , self.__byte[cnt_byte : cnt_byte + 4])[0]
        self.__zScale = struct.unpack(f'{BYTE_ORDER}L' , self.__byte[cnt_byte + 4 : cnt_byte + 8])[0]
        self.__iBBMode = struct.unpack(f'{BYTE_ORDER}L' , self.__byte[cnt_byte + 8 : cnt_byte + 12])[0]
        return {'zHt': self.__zHt , 'zScale': self.__zScale , 'iBBMode': self.__iBBMode}

    def getZHt(self):
        return self.__zHt

    def getZScale(self):
        return self.__zScale

    def getIBBMode(self):
        return self.__iBBMode

    def getInfo(self):
        cnt_para = HEADER_LENGTH + self.__zNum + 11
        cnt_byte = cnt_para * 4
        # self.__varName = ''.join([chr(self.__byte[cnt_b]) for cnt_b in range(cnt_byte , cnt_byte + 20)]).strip('\x00')
        # self.__varUnits = ''.join([chr(self.__byte[cnt_b]) for cnt_b in range(cnt_byte + 20 , cnt_byte + 26)]).strip('\x00')
        self.__varName = struct.unpack('20s' , self.__byte[cnt_byte : cnt_byte + 20])[0].decode().strip('\x00')
        self.__varUnits = struct.unpack('6s' , self.__byte[cnt_byte + 20 : cnt_byte + 26])[0].decode().strip('\x00')

        cnt_byte += 26
        self.__varScale = struct.unpack(f'{BYTE_ORDER}L' , self.__byte[cnt_byte : cnt_byte + 4])[0]
        self.__missingValue = struct.unpack(f'{BYTE_ORDER}l' , self.__byte[cnt_byte + 4 : cnt_byte + 8])[0]
        self.__radarNum = struct.unpack(f'{BYTE_ORDER}L' , self.__byte[cnt_byte + 8 : cnt_byte + 12])[0]

        # Mosaic Radars
        cnt_byte += 12
        self.__radarName = []
        if self.__radarNum != 0:
            for cnt_rad in range(self.__radarNum):
                self.__radarName.append(struct.unpack('4s' , self.__byte[cnt_byte + cnt_rad * 4 : cnt_byte + cnt_rad * 4 + 4])[0].decode())

        return {'varName': self.__varName , 'varUnits': self.__varUnits , 
                'varScale': self.__varScale , 'missingValue': self.__missingValue , 
                'radarNum': self.__radarNum , 'radarName': self.__radarName}
    
    def getVarName(self):
        return self.__varName

    def getVarUnits(self):
        return self.__varUnits

    def getVarScale(self):
        return self.__varScale

    def getMissingValue(self):
        return self.__missingValue

    def getRadarNum(self):
        return self.__radarNum

    def getRadarName(self):
        return self.__radarName

    def getData(self):
        cnt_byte = (HEADER_LENGTH + self.__zNum + 11) * 4 + 38 + self.__radarNum * 4
        self.__data = np.empty([self.__xNum , self.__yNum])
        for cnt_z in range(self.__zNum):    # Need to Revised Code if z-Layer is not Equal to 1 
            for cnt_y in range(self.__yNum):
                for cnt_x in range(self.__xNum):
                    self.__data[cnt_x , cnt_y] = struct.unpack(f'{BYTE_ORDER}h' , self.__byte[cnt_byte : cnt_byte + 2])[0] / self.__varScale
                    if self.__data[cnt_x , cnt_y] == self.__missingValue:
                        self.__data[cnt_x , cnt_y] = np.nan
                    cnt_byte += 2
        return self.__data

def gunzipAndReadByte(fPath):
    if str(fPath)[-3:] == '.gz':
        f = gzip.GzipFile(mode = 'rb' , fileobj = open(fPath , 'rb'))
    else:
        f = open(fPath , 'rb')
    return f.read()