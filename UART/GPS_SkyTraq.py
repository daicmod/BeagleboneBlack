#
# SkyTraq製GPSモジュールのテスト用ソースコード
# Author:	Daisuke Morita
# Created:	24.03.2019
#

import serial
import time

# UART番号を選択
com_serial = serial.Serial('/dev/serial0', 115200, timeout=10)

while True:
	SKYTRAQ_FORMAT = b'\xA0\xA1'	
	NMEA_FORMAT = b'$G'
	END_FORMAT = b'\x0D\x0A'

	# GPSデータを1行分取得
	tmp = com_serial.readline()

	if SKYTRAQ_FORMAT in tmp and END_FORMAT in tmp:
		# SKYTRAQ準拠のバイナリデータが格納されている行
		print(tmp.hex())
	elif NMEA_FORMAT in tmp and END_FORMAT in tmp:
		# NMEAフォーマットのデータが格納されている行
		print(tmp.decode(utf-8''))