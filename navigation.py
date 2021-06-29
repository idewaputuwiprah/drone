import socket
import sys
import time
import threading
import subprocess
import bluetooth
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
modeHome = False
switch = False
isError = False
isSendByUser = True
isEmergencyLand = False

point2 = []
pointHome = []
initDistance = -999.0
totalDistance = 0

def timeOut():
    global canSendCommand
    while True:
        try:
            while canSendCommand == True:
                pass
            print("can send command {}".format(canSendCommand))
            time.sleep(8)
            if canSendCommand == False or isError == True:
                print("resendCommand")
                if drone.lastCommand != "":
                    if "forward" not in drone.lastCommand and "cw" not in drone.lastCommand:
                        drone.sendCommand(drone.lastCommand, sock)
        except Exception:
            break

def recv():
    global canSendCommand
    global canRecvCommand
    global isError
    while True: 
        try:
            canRecvCommand = True
            data, server = sock.recvfrom(1518)
            canRecvCommand = False
            status = data.decode(encoding="utf-8")
            
            if status == "ok":
                isError = False
                print("status is ok")
                drone.lastCommand = ""
                canSendCommand = True
            elif "error" in status:
                isError = True
                print("status error: {}\n".format(status))
            else:
                isError = False
                print("status any: {}\n".format(status))
                canSendCommand = True
        except KeyboardInterrupt:
            break
        except Exception as inst:
            print("Exception...")
            print(type(inst))
            print(inst.args)

def bluetoothCommand():
    global isSendByUser
    global isEmergencyLand
    global point2
    global pointHome
    server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    port = bluetooth.PORT_ANY
    server_sock.bind(("",port))
    server_sock.listen(1)
    print("listening on port {}".format(port))

    uuid = "1e0ca4ea-299d-4335-93eb-27fcfe7fa848"
    bluetooth.advertise_service( server_sock, "Drone Service", uuid )

    while True:
        print("Waiting for client to connect...")
        client_sock,address = server_sock.accept()
        print("Accepted connection from {}".format(address))

        while True:
            try:
                print("Waiting data...")
                data = client_sock.recv(1024)
                msg = data.decode("utf-8")
                if ',' in msg:
                    points = msg.split(",")
                    if len(points) == 4:
                        pointHome.append(float(points[0]))
                        pointHome.append(float(points[1]))
                        point2.append(float(points[2]))
                        point2.append(float(points[3]))
                        isSendByUser = True
                    else:
                        print("length: {}".format(len(points)))
                else:
                    print("received [{}]".format(msg))
                    if 'emergency' in msg:
                        isEmergencyLand = True
            except Exception as exc:
                print("Bluetoosh exception {}: {}".format(type(exc), exc.args))
                client_sock.close()
                break

def getBattery():
    global canSendCommand
    drone.getBattery(sock)
    while canSendCommand == False or canRecvCommand == False:
        pass
    time.sleep(0.5)

def moveUp(up):
    drone.moveUp(up, sock)

def checkDroneBearing(locBearing):
    global canSendCommand
    while True:
        droneBearing = abs(compass.getDroneBearing())
        if abs(droneBearing-locBearing) >= 5:
            setDroneHeading(droneBearing, locBearing)
            canSendCommand = False
        else:
            break
        while canSendCommand == False or canRecvCommand == False:
            pass
        time.sleep(0.5)

def setDroneHeading(droneBearing, locBearing):
    global canSendCommand
    if droneBearing > locBearing:
        deg = droneBearing - locBearing
        drone.moveCounterClockWise(floor(deg), sock)
    else:
        deg = locBearing - droneBearing
        drone.moveClockWise(floor(deg), sock)

def switchDestination():
    global point2
    point2[0] = pointHome[0]
    point2[1] = pointHome[1]

def main():
    timeoutThread = threading.Thread(target=timeOut)
    timeoutThread.daemon = True
    timeoutThread.start()
    btThread = threading.Thread(target=bluetoothCommand)
    btThread.daemon = True
    btThread.start()
    while True:
        global canSendCommand
        global initDistance
        global totalDistance
        global modeHome
        global switch
        global isSendByUser
        global isEmergencyLand
        if isEmergencyLand == True:
            drone.landing(sock)
            print("Landing...")
            canSendCommand = False
            while True:
                if canSendCommand==True and canRecvCommand==True:
                    time.sleep(0.5)
                    drone.stopMotor(sock)
                    break
            isSendByUser = False
            isEmergencyLand = False
        if modeHome == True and switch == False:
            switchDestination()
            canSendCommand = True
            switch = True
        try:
            if canSendCommand==True and canRecvCommand==True and isSendByUser==True:
                time.sleep(0.5)
                if drone.initMode:
                    drone.sdkMode(sock)
                else:
                    if drone.status == drone.landStatus:
                        getBattery()
                        drone.takeoff(sock)
                        canSendCommand = False
                        while True:
                            if canSendCommand==True and canRecvCommand==True:
                                moveUp(40)
                                break
                    else:
                        distance, locBearing = gps.calculateDistance(point2[0], point2[1])
                        if initDistance < 0:
                            initDistance = distance
                            totalDistance = distance
                        if distance > totalDistance and totalDistance >= 0:
                            distance = floor(totalDistance)
                        if distance <= 0.5 or totalDistance <= 0.0:
                            drone.atDest = True
                        if drone.atDest == True:
                            drone.landing(sock)
                            canSendCommand = False
                            while True:
                                if canSendCommand==True and canRecvCommand==True:
                                    time.sleep(0.5)
                                    getBattery()
                                    drone.stopMotor(sock)
                                    break
                            if modeHome == True:
                                break
                            else:
                                initDistance = -999.0
                                totalDistance = 0
                                drone.atDest = False
                                modeHome = True
                            time.sleep(7)
                        else:
                            checkDroneBearing(abs(locBearing))
                            dist = 0.0
                            if distance >= 5:
                                drone.moveForward(500, sock)
                                dist = 5.0
                            else:
                                drone.moveForward(floor(distance)*100, sock)
                                dist = distance
                            totalDistance = totalDistance - dist
                canSendCommand = False
        except KeyboardInterrupt:
            print("interrupt")
            sys.exit

if __name__ == "__main__":
    subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])
    recvThread = threading.Thread(target=recv)
    recvThread.daemon = True
    recvThread.start()
    main()
