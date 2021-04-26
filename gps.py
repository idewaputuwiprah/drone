import io

import pynmea2
import serial
from math import cos, sin, sqrt, pow, radians, tan, atan, atan2, degrees
from pygeodesy import hubeny, haversine, vincentys

class Gps:

    r2 = 6371008.77141
    ser = serial.Serial('/dev/serial0', 9600, timeout=0.5)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    # point2 = [-6.58826252783985, 106.7591997268015]

    def vincenty_formula(self, latitude1, longitude1, latitude2, longitude2):
        numerator = ( (cos(latitude2) * sin(longitude2-longitude1)) * (cos(latitude2) * sin(longitude2-longitude1)) ) + ( (cos(latitude1) * sin(latitude2) - sin(latitude1) * cos(latitude2) * cos(longitude2-longitude1)) * (cos(latitude1) * sin(latitude2) - sin(latitude1) * cos(latitude2) * cos(longitude2-longitude1)))
        denominator = sin(latitude1) * sin(latitude2) + cos(latitude1) * cos(latitude2) * cos(longitude2-longitude1)
        distance = self.r2 * atan(sqrt(numerator)/denominator)
        return distance
    
    def calculateBearing(self, init, dest):
        dL = dest[1] - init[1]
        x = cos(dest[0]) * sin(dL)
        y = cos(init[0]) * sin(dest[0]) - sin(init[0]) * cos(dest[0]) * cos(dL)
        return atan2(x,y)

    def calculateDistance(self, latitude2, longitude2):
        while 1:
            try:
                line = self.sio.readline()
                if line.find('GGA') > 0:
                    msg = pynmea2.parse(line)
                    start = [msg.latitude, msg.longitude]
                    dest = [latitude2, longitude2]
                    # print(str(msg.latitude) + "," + str(msg.longitude))
                    distance = self.vincenty_formula(radians(msg.latitude), radians(msg.longitude), radians(latitude2), radians(longitude2))
                    bearing = self.calculateBearing(start, dest)
                    return distance, abs(degrees(bearing)), msg.num_sats
                    break
            except serial.SerialException as e:
                print('Device error: {}'.format(e))
                return 0.0
                break
            except pynmea2.ParseError as e:
                print('Parse error: {}'.format(e))
                continue
            except UnicodeDecodeError:
                continue
    
