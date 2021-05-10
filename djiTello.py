class DjiTello:
    initMode = True
    atDest = False
    landStatus = "land"
    takeoffStatus = "takeoff"

    def __init__(self, address='192.168.10.1', port=8889):
        self.address = (address, port)
        self.status = self.landStatus
    
    def sdkMode(self, sock):
        if self.initMode:
            msg = "command"
            self.sendCommand(msg, sock)
            self.initMode = False
        else: 
            print("Alredy in sdk mode")
    
    def takeoff(self, sock):
        if self.initMode == False:
            msg = "takeoff"
            self.status = self.takeoffStatus
            self.atDest = False
            self.sendCommand(msg, sock)
        else:
           self.printError() 
    
    def landing(self, sock):
        if self.initMode == False:
            msg = "land"
            self.status = self.landStatus
            self.sendCommand(msg, sock)
        else:
            self.printError()
    
    def stopMotor(self, sock):
        if self.initMode == False:
            msg = "emergency"
            self.sendCommand(msg, sock)
    
    def moveForward(self, distance, sock):
        if self.initMode == False:
            msg = "forward " + str(distance)
            self.sendCommand(msg, sock)
        else:
            self.printError()
    
    def moveClockWise(self, degree, sock):
        if self.initMode == False:
            msg = "cw " + str(degree)
            self.sendCommand(msg, sock)
        else:
            self.printError()

    def moveCounterClockWise(self, degree, sock):
        if self.initMode == False:
            msg = "ccw " + str(degree)
            self.sendCommand(msg, sock)
        else:
            self.printError()

    def getBattery(self, sock):
        if self.initMode == False:
            msg = "battery?"
            self.sendCommand(msg, sock)
        else:
            self.printError()
    
    def sendCommand(self, msg, sock):
        command = msg.encode(encoding="utf-8")
        print(command)
        sent = sock.sendto(command, self.address)
    
    def printError(self):
        print("Not in sdk mode")
