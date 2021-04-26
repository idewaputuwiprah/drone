import py_qmc5883l
from time import sleep

class Compass:
    sensor = py_qmc5883l.QMC5883L()
    sensor.calibration = [[1.0312611143704742, -0.02948626830605866, 211.78815328747538], [-0.02948626830605866, 1.0278121889166578, 972.2286540766696], [0.0, 0.0, 1.0]]
    #sensor.declination = 77.0
    sensor.declination = -115.0

    def getDroneBearing(self):
        # print(sensor.get_magnet_raw())
        bearing = self.sensor.get_bearing()
        return bearing
