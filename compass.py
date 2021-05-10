import py_qmc5883l
from time import sleep

class Compass:
    sensor = py_qmc5883l.QMC5883L()
    sensor.calibration = [[1.1352465595691261, -0.114933719907172, 106.89451922307947], [-0.114933719907172, 1.0976716894964607, -84.55505613724887], [0.0, 0.0, 1.0]]
    #sensor.declination = 77.0
    sensor.declination = -90.0

    def getDroneBearing(self):
        # print(sensor.get_magnet_raw())
        bearing = self.sensor.get_bearing()
        return bearing
