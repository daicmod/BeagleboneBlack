from SD import SDCardController
import threading
import time

# To control SD card for bit error measurement 
class XRayDetector(SDCardController):
	def __init__(self, spi):
		super().__init__(spi)
		
		self.block_num = 0
		self.error_counter = 0
		self.return_error_counter = 0
		self.measurement_blocks_len = self.sectors * 1024
		self.measurement_flag = True

	# To start the measurement thread(async, daemon)
	# return: thread.is_alived()
	def start_measurement(self):		
		self.start = time.time()
		self.measure_th = threading.Thread(target = self._measurement_error_async_daemon, daemon = True)
		self.measure_th.start()
		return measure_th.is_alive():

	# To stop the measurement thread
	# When the timeout argument is present and not None, it should be a floating point number specifying a timeout for the operation in seconds (or fractions thereof).
	# return: thread.is_alived()
	def stop_measurement(self, timeout = None):
		self.measurement_flag = False
		self.measure_th.join(timeout)
		self.error_counter = 0
		self.block_num = 0
		return measure_th.is_alive()

	# To get the measurement result now
	# return: int type
	def get_count(self):
		return self.return_error_counter

	# To reset the measurement result
	# Don't stop the thread
	def reset_count(self):
		self.return_error_counter = 0
		self.error_counter = 0

	# To get the complete rate of the measurement
	# return: [percentage, elapsed time]
	def get_complete_rate(self):
		complete_rate = self.block_num / (self.measurement_blocks_len) * 100
		elapsed_time = time.time() - self.start
		return [complete_rate, elapsed_time]

	# To set the measurement range(Default: Overall measurement)
	# lenth: Please set a Multiple of 64(None or More than the maximum value: Overall measurement)
	def set_measurement_blocks_len(self, lenth = self.sectors * 1024):
		assert not lenth % 64, 'length is invalid'
		if lenth > self.sectors * 1024:
			lenth = self.sectors * 1024
		self.measurement_blocks_len = lenth

	# main measurement loop
	def _measurement_error_async_daemon(self):
		self.block_num = 0
		while self.measurement_flag:
			self._count_error(self.block_num)
			self.return_error_counter = self.error_counter
			self.block_num += 64
			if self.block_num >= self.measurement_blocks_len:
				return
	
	# To count number of error in 64block
	# Initialize the measured block
	# block_num: start block 
	def _count_error(self, block_num):
		buf = self._read_64blocks(block_num)		
		for v in buf:
			self.error_counter += (format(v, "b").zfill(8).count("0"))
		self._reset_64blocks(block_num)

	# To read 64 blocks in SD card
	# block_num: start block
	def _read_64blocks(self, block_num):
		buf_len = 64 * 512
		buf = [0x00] * buf_len
		buf = super().read_blocks(block_num, buf)		
		return buf

	# To reset 64 blocks in SD card
	# block_num: start block
	def _reset_64blocks(self, block_num):
		buf_len = 64 * 512
		buf = [0xff] * buf_len
		super().write_blocks(block_num, buf)
