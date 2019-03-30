import time

_CMD_TIMEOUT = 10

_R1_IDLE_STATE = 1 << 0
#R1_ERASE_RESET = const(1 << 1)
_R1_ILLEGAL_COMMAND = 1 << 2
#R1_COM_CRC_ERROR = const(1 << 3)
#R1_ERASE_SEQUENCE_ERROR = const(1 << 4)
#R1_ADDRESS_ERROR = const(1 << 5)
#R1_PARAMETER_ERROR = const(1 << 6)
_TOKEN_CMD25 = 0xfc
_TOKEN_STOP_TRAN = 0xfd
_TOKEN_DATA = 0xfe


class SDCardController:
	def __init__(self, spi):
		self.spi = spi		

		self.tokenbuf = [0xff]

		# initialise the card
		self._init_card()

	def _init_card(self):
		# init SPI bus; use low data rate for initialisation
		self.spi.mode = 0b00
		self.spi.msh = 100 * 1000

		# clock card at least 100 cycles with cs high
		for i in range(16):
			self.spi.writebytes([0xff])

		# CMD0: init card; should return _R1_IDLE_STATE (allow 5 attempts)
		for _ in range(5):
			r = self._cmd(0, 0, 0x95)
			if r == _R1_IDLE_STATE:
				break
			else:
				raise OSError("no SD card")

		# CMD8: determine card version
		r = self._cmd(8, 0x01aa, 0x87, 4)
		if r == _R1_IDLE_STATE:
			self._init_card_v2()
		elif r == (_R1_IDLE_STATE | _R1_ILLEGAL_COMMAND):
			self._init_card_v1()
		else:
			raise OSError("couldn't determine SD card version")

		# get the number of sectors
		# CMD9: response R2 (R1 byte + 16-byte block read)
		r = self._cmd(9, 0, 0, 0, False)		
		if r != 0:
			raise OSError("no response from SD card")
		csd = [0x00] * 16
		csd = self._readinto(csd)

		if csd[0] & 0xc0 == 0x40: # CSD version 2.0
			#print("CSD version 2.0")
			#self.sectors = ((csd[8] << 8 | csd[9]) + 1) * 512 * 1024
			self.sectors = (csd[7] & 0x7f) << 16 | csd[8] << 8 | csd[9]
			self.sectors = (self.sectors + 1)
		elif csd[0] & 0xc0 == 0x00: # CSD version 1.0 (old, <=2GB)
			#print("CSD version 1.0")
			r_bl_len = csd[5] & 0b1111
			c_size = csd[6] & 0b11 | csd[7] << 2 | (csd[8] & 0b11000000) << 4
			c_size_mult = ((csd[9] & 0b11) << 1) | csd[10] >> 7
			self.sectors = (c_size + 1) * (2 ** (c_size_mult + 2))
		else:
			raise OSError("SD card CSD format not supported")
		# print('SD_SIZE', (self.sectors / 1024 / 1024 / 1024), 'GB')

		# CMD16: set block length to 512 bytes
		if self._cmd(16, 512, 0) != 0:
			raise OSError("can't set 512 block size")

		# set to high data rate now that it's initialised
		self.spi.msh = 64 * 1024 * 1024

	def _init_card_v1(self):
		for i in range(_CMD_TIMEOUT):
			self._cmd(55, 0, 0)
			if self._cmd(41, 0, 0) == 0:
				self.cdv = 512
				#print("[SDCard] v1 card")
				return
		raise OSError("timeout waiting for v1 card")

	def _init_card_v2(self):
		for i in range(_CMD_TIMEOUT):
			time.sleep(0.050)
			self._cmd(58, 0, 0, 4)
			self._cmd(55, 0, 0)
			if self._cmd(41, 0x40000000, 0) == 0:
				self._cmd(58, 0, 0, 4)
				self.cdv = 1
				#print("[SDCard] v2 card")
				return
		raise OSError("timeout waiting for v2 card")

	def _cmd(self, cmd, arg, crc, final=0, release=True, skip1=False):
		# create and send the command
		buf = [0x40 | cmd, arg >> 24, arg >> 16, arg >> 8, arg, crc]
		self.spi.writebytes(buf)

		if skip1:
			self.tokenbuf = self.spi.xfer2([0xff])

		# wait for the response (response[7] == 0)
		for i in range(_CMD_TIMEOUT):
			self.tokenbuf = self.spi.xfer2([0xff])
			response = self.tokenbuf[0]
			if not (response & 0x80):
				# this could be a big-endian integer that we are getting here
				for j in range(final):
					self.spi.writebytes([0xff])
				if release:
					self.spi.writebytes([0xff])
				return response
		# timeout
		self.spi.writebytes([0xff])
		return -1

	def _readinto(self, buf):
		# read until start byte (0xff)
		while True:
			self.tokenbuf = self.spi.xfer2([0xff])
			if self.tokenbuf[0] == _TOKEN_DATA:
				break

		# read data
		mv = [0xff] * len(buf)
		buf = self.spi.xfer2(mv)

		# read checksum
		self.spi.writebytes([0xff])
		self.spi.writebytes([0xff])

		#self.spi.writebytes([0xff])

		return buf

	def _write(self, token, buf):
		# send: start of block, data, checksum
		self.spi.xfer2(token)
		self.spi.writebytes(buf)
		self.spi.writebytes([0xff])
		self.spi.writebytes([0xff])

		# check the response
		if (self.spi.xfer2([0xff])[0] & 0x1f) != 0x05:
			self.spi.writebytes([0xff])
			return

		# wait for write to finish
		while self.spi.xfer2([0xff])[0] == 0:
			pass

		self.spi.writebytes([0xff])

	def _write_token(self, token):
		self.spi.xfer2(token)
		self.spi.writebytes([0xff])
		# wait for write to finish
		while self.spi.xfer2([0xff])[0] == 0x00:
			pass

		self.spi.writebytes([0xff])

	def read_blocks(self, block_num, buf):
		nblocks = len(buf) // 512
		assert nblocks and not len(buf) % 512, 'Buffer length is invalid'
		if nblocks == 1:
			# CMD17: set read address for single block
			if self._cmd(17, block_num * self.cdv, 0, release=False) != 0:
				# release the card
				raise OSError(5) # EIO
			# receive the data and release card
			buf = self._readinto(buf)
			return buf
		else:
			# CMD18: set read address for multiple blocks
			if self._cmd(18, block_num * self.cdv, 0, release=False) != 0:
				# release the card
				raise OSError(5) # EIO
			offset = 0
			mv = buf
			while nblocks:
				# receive the data and release card
				buf[offset : offset + 512] = self._readinto(mv[offset : offset + 512])
				offset += 512
				nblocks -= 1
			if self._cmd(12, 0, 0xff, skip1=True):
				raise OSError(5) # EIO
			return buf


	def write_blocks(self, block_num, buf):
		#nblocks = len(buf) // 512
		#assert nblocks and not len(buf) % 512, 'Buffer length is invalid'
		nblocks, err = divmod(len(buf), 512)
		assert nblocks and not err, 'Buffer length is invalid'
		if nblocks == 1:
			# CMD24: set write address for single block
			if self._cmd(24, block_num * self.cdv, 0) != 0:
				raise OSError(5) # EIO

			# send the data
			self._write([_TOKEN_DATA], buf)
		else:
			# CMD25: set write address for first block
			r = self._cmd(25, block_num * self.cdv, 0)
			while True:
				if r == 0:
					break
				r = self._cmd(25, block_num * self.cdv, 0)

			# send the data
			offset = 0
			mv = buf
			while nblocks:
				self._write([_TOKEN_CMD25], mv[offset : offset + 512])
				offset += 512
				nblocks -= 1
			self._write_token([_TOKEN_STOP_TRAN])

	def get_sectors(self):
		return self.sectors