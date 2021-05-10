import io

import time
import threading
import pynmea2
import serial
from math import cos, sin, sqrt, pow, radians, tan, atan, atan2, degrees
from pygeodesy import hubeny, haversine, vincentys

class Gps:

    r2 = 6371008.77141
    ser = serial.Serial('/dev/serial0', 9600, timeout=0.5)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    timeout = False
    loc26 = []
    locNone = []
    FILE = "/home/pi/drone/project/rawData.txt"

    def write(self, text):
        with open(self.FILE, 'a') as f:
            f.write(text)

    def delay(self):
            time.sleep(5.5)
            self.timeout = True

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
        start = []
        dest = [latitude2, longitude2]
        delayThread = threading.Thread(target=self.delay)
        delayThread.start()
        lat = 0.0
        lon = 0.0
        while self.timeout == False:
            try:
                line = self.sio.readline()
                if line.find('GGA') > 0:
                    self.write("{}".format(line))
                    msg = pynmea2.parse(line)
                    if int(msg.num_sats) == 26:
                        self.loc26.append([msg.latitude, msg.longitude])
                    else:
                        self.locNone.append([msg.latitude, msg.longitude])
                    # distance = self.vincenty_formula(radians(msg.latitude), radians(msg.longitude), radians(latitude2), radians(longitude2))
                    # bearing = self.calculateBearing(start, dest)
                    # return distance, abs(degrees(bearing)), msg.num_sats
                    # break
            except serial.SerialException as e:
                print('Device error: {}'.format(e))
                return -10000.0
                break
            except pynmea2.ParseError as e:
                print('Parse error: {}'.format(e))
                continue
            except UnicodeDecodeError:
                continue

        self.timeout = False

        if len(self.loc26) > 0:
            for coord in self.loc26:
                lat = lat + coord[0]
                lon = lon + coord[1]
            start.append(lat/len(self.loc26))
            start.append(lon/len(self.loc26))
        else:
            for coord in self.locNone:
                lat = lat + coord[0]
                lon = lon + coord[1]
            start.append(lat/len(self.locNone))
            start.append(lon/len(self.locNone))
        print(start)
        distance = self.vincenty_formula(radians(start[0]), radians(start[1]), radians(dest[0]), radians(dest[1]))
        bearing = self.calculateBearing(start, dest)
        return distance, abs(degrees(bearing))
    
