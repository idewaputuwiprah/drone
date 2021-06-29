import py_qmc5883l
from time import sleep

class Compass:
    sensor = py_qmc5883l.QMC5883L()
    sensor.calibration = [[1.0069673106642365, -0.01389930772600162, 89.97110320012038], [-0.01389930772600162, 1.0277281672329814, -72.81102376470415], [0.0, 0.0, 1.0]]
    sensor.declination = -95.0

    def getDroneBearing(self):
        bearing = self.sensor.get_bearing()
        return bearing
