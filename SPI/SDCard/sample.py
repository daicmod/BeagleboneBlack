from XRayDetector import XRayDetector
from Adafruit_BBIO.SPI import SPI
import time

spi = SPI(1, 0)
xray = XRayDetector(spi)

xray.start_measurement()
time.sleep(30)
xray.stop_measurement()

print(xray.get_count())
