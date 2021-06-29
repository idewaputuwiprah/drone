import io
import time
import threading
import pynmea2
import serial
from math import cos, sin, sqrt, pow, radians, tan, atan, atan2, degrees

class Gps:
    r2 = 6371008.77141
    ser = serial.Serial('/dev/serial0', 9600, timeout=0.5)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    timeout = False
    loc = []

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
        self.loc.clear()
        lat = 0.0
        lon = 0.0
        delayThread = threading.Thread(target=self.delay)
        delayThread.start()
        while self.timeout == False:
            try:
                line = self.sio.readline()
                if line.find('GGA') > 0:
                    msg = pynmea2.parse(line)
                    if msg.latitude != 0.0 and msg.longitude != 0.0:
                        self.loc.append([msg.latitude, msg.longitude])
            except serial.SerialException as e:
                print('Device error: {}'.format(e))
                break
            except pynmea2.ParseError as e:
                print('Parse error: {}'.format(e))
                continue
            except UnicodeDecodeError:
                continue

        self.timeout = False
        print("len loc: {}".format(len(self.loc)))

        for coord in self.loc:
            lat = lat + coord[0]
            lon = lon + coord[1]
        start.append(lat/len(self.loc))
        start.append(lon/len(self.loc))
        print(start)
        distance = self.vincenty_formula(radians(start[0]), radians(start[1]), radians(dest[0]), radians(dest[1]))
        bearing = self.calculateBearing(start, dest)
        normalizeBearing = (degrees(bearing) + 360) % 360
        return distance, normalizeBearing
    
