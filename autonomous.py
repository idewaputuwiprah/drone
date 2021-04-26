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

point2 = [-6.588425,106.75856]

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

def setDroneHeading(droneBearing, locBearing):
    global canSendCommand
    if droneBearing > locBearing:
        deg = droneBearing - locBearing
        drone.moveCounterClockWise(floor(deg), sock)
    else:
        deg = locBearing - droneBearing
        drone.moveClockWise(floor(deg), sock)
    drone.atDest = True

def main():
    while True:
        global canSendCommand
        try:
            if canSendCommand==True and canRecvCommand==True:
                time.sleep(0.5)
                if drone.initMode:
                    # write("SDK MODE\n")
                    drone.sdkMode(sock)
                else:
                    # calculate distance
                    # calculate bearing
                    distance, locBearing, sats = gps.calculateDistance(point2[0], point2[1])
                    droneBearing = compass.getDroneBearing()
                    if drone.status == drone.landStatus:
                        # write("TAKEOFF\n")
                        drone.takeoff(sock)
                    else:
                        if drone.atDest == True:
                            # write("LAND\n")
                            drone.landing(sock)
                            print("Landing...")
                            canSendCommand = False
                            while True:
                                if canSendCommand==True and canRecvCommand==True:
                                    time.sleep(0.5)
                                    # write("STOP MOTOR\n")
                                    drone.stopMotor(sock)
                                    break
                            break
                        else:
                            # write("MUTER\n")
                            setDroneHeading(droneBearing, locBearing)
                    # else: 
                    # check if distance < 1 then land
                    # else check rotation cw or ccw, if distance > 5m, forward 500 else forward distance
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
