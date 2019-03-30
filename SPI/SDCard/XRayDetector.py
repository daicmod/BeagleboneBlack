from SD import SDCardController
import threading
import time

class XRayDetector(SDCardController):
	def __init__(self, spi):
		super().__init__(spi)
		
		self.block_num = 0
		self.error_counter = 0
		self.return_error_counter = 0
		self.measurement_blocks_len = self.sectors * 1024
		self.measurement_flag = True

	def start_measurement(self):
		self.start = time.time()
		self.measure_th = threading.Thread(target = self._measurement_error_thread)
		self.measure_th.start()
		return True

	def stop_measurement(self):
		self.measurement_flag = False
		self.measure_th.join()
		self.error_counter = 0
		self.block_num = 0
		return True

	def get_count(self):
		return self.return_error_counter

	def reset_count(self):
		self.return_error_counter = 0
		self.error_counter = 0

	def get_complete_rate(self):
		complete_rate = self.block_num / (self.measurement_blocks_len) * 100
		elapsed_time = time.time() - self.start
		return [complete_rate, elapsed_time]

	def set_measurement_blocks_len(self, lenth):
		assert not lenth % 64, 'length is invalid'
		self.measurement_blocks_len = lenth

	def _measurement_error_thread(self):
		self.block_num = 0
		while self.measurement_flag:
			self._count_error(self.block_num)
			self.return_error_counter = self.error_counter
			self.block_num += 64
			if self.block_num >= self.measurement_blocks_len:
				break
		
	def _count_error(self, block_num):
		buf = self._read_64blocks(block_num)		
		for v in buf:
			self.error_counter += (format(v, "b").zfill(8).count("0"))
		self._reset_64blocks(block_num)

	def _read_64blocks(self, block_num):
		buf_len = 64 * 512
		buf = [0x00] * buf_len
		buf = super().read_blocks(block_num, buf)		
		return buf

	def _reset_64blocks(self, block_num):
		buf_len = 64 * 512
		buf = [0xff] * buf_len
		super().write_blocks(block_num, buf)
