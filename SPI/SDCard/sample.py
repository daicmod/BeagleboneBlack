from XRayDetector import XRayDetector
from Adafruit_BBIO.SPI import SPI
import time

spi = SPI(1, 0)
xray = XRayDetector(spi)

xray.set_measurement_blocks_len(xray.get_sectors() * 1024)

while not xray.start_measurement():
	time.sleep(1)

while True:
	tmp = xray.get_complete_rate()
	print(tmp)	
	if tmp[0] == 100:
		break
	time.sleep(3)

while xray.stop_measurement():
	time.sleep(1)

print(xray.get_count())
