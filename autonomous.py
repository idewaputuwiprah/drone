import socket
import sys
import time
import threading
from djiTello import DjiTello
from gps import Gps
from compass import Compass
from math import floor

host = ''
port = 9000
locaddr = (host,port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(locaddr)
drone = DjiTello()

gps = Gps()
compass = Compass()

canSendCommand = True
canRecvCommand = False

# locBearing = 126.99778403250419
# distance = 4.1258092453538096
# droneBearing = 342.2202850758707

point2 = [-6.557247033333333,106.73343356666685]
initDistance = -999.0
totalDistance = 0

FILE = "/home/pi/drone/project/log.txt"

def write(text):
    with open(FILE, 'a') as f:
        f.write(text)

def recv():
    global canSendCommand
    global canRecvCommand
    while True: 
        try:
            # write("Waiting for response...\n")
            canRecvCommand = True
            data, server = sock.recvfrom(1518)
            canRecvCommand = False
            status = data.decode(encoding="utf-8")
            # write("This is status {}\n".format(status))
            if status == "ok":
                print("status is ok")
                canSendCommand = True
            elif status == "error":
                print("status is error")
            else:
                print(status)
                canSendCommand = True
        except KeyboardInterrupt:
            break
        except Exception:
            # print ('\nExit . . .\n')
            break

def checkDroneBearing(droneBearing, locBearing):
    global canSendCommand
    if abs(droneBearing-locBearing) >= 1:
        setDroneHeading(droneBearing, locBearing)
        canSendCommand = False
    while canSendCommand == False or canRecvCommand == False:
        pass

def setDroneHeading(droneBearing, locBearing):
    global canSendCommand
    if droneBearing > locBearing:
        deg = droneBearing - locBearing
        drone.moveCounterClockWise(floor(deg), sock)
    else:
        deg = locBearing - droneBearing
        drone.moveClockWise(floor(deg), sock)
    # drone.atDest = True

def main():
    while True:
        global canSendCommand
        global initDistance
        global totalDistance
        try:
            if canSendCommand==True and canRecvCommand==True:
                time.sleep(0.5)
                if drone.initMode:
                    drone.sdkMode(sock)
                else:
                    distance, locBearing = gps.calculateDistance(point2[0], point2[1])
                    droneBearing = compass.getDroneBearing()
                    if initDistance < 0:
                        initDistance = distance
                    if distance <= 5 or totalDistance >= initDistance:
                        drone.atDest = True
                    if drone.status == drone.landStatus:
                        drone.takeoff(sock)
                    else:
                        checkDroneBearing(droneBearing, locBearing)
                        if drone.atDest == True:
                            drone.landing(sock)
                            print("Landing...")
                            canSendCommand = False
                            while True:
                                if canSendCommand==True and canRecvCommand==True:
                                    time.sleep(0.5)
                                    drone.stopMotor(sock)
                                    break
                            break
                        else:
                            # setDroneHeading(droneBearing, locBearing)
                            # drone maju ke depan distance x 100
                            if distance >= 5:
                                drone.moveForward(500, sock)
                            else:
                                drone.moveForward(distance*100, sock)
                            totalDistance = totalDistance + distance
                canSendCommand = False
        except KeyboardInterrupt:
            print("interrupt")
            sys.exit

if __name__ == "__main__":
    # write("TRY PROGRAM\n")
    recvThread = threading.Thread(target=recv)
    recvThread.daemon = True
    recvThread.start()
    main()
