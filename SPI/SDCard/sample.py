from XRayDetector import XRayDetector
from Adafruit_BBIO.SPI import SPI
import time

spi = SPI(1, 0)
xray = XRayDetector(spi)

while not xray.start_measurement():
	time.sleep(1)
time.sleep(10)
while not xray.stop_measurement():
	time.sleep(1)

print(xray.get_count())
