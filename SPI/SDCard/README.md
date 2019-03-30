Control of the SD card using the SPI.

XRayDetector(SDCardController)
SD�J�[�h���g���ăr�b�g���]�����o���邽�߂ɊJ���������C�u�����ł��D
SDCardController���p�����Ă��܂��D
�C���X�^���X�̐������@��SDCardController�ɓ����ł��D

start_measurement()
	SD�J�[�h�����r�b�g���]���Ă��邩�v������񓯊��������J�n���܂��D
	1���[�v������64�u���b�N�ǂݏo���āC�ǂݏo�����r�b�g���S��1�ɖ߂��������s���Ă��܂��D
	32GB��S�Čv������ɂ�120���Ԓ��x������Ǝv���܂��D	

stop_measurement()
	start_measurement()�ŊJ�n�����񓯊��������I�����܂��D
	�Ăяo���Ă��猻�ݓǂݏo���Ă���u���b�N�����ǂݏI����Ă���C�c��̃u���b�N���Ɋւ�炸�I�����܂��D
	�������I����Ă��邱�Ƃ������ł��X���b�h��join���Ă���ꏊ�Ȃ̂ŕK���Ăяo���Ă����Ă��������D

get_count()
	���݂̃G���[�r�b�g����Ԃ��܂��D
	�v�����I�����Ă���Ăяo���Ȃ��ƈӖ��Ȃ��C�����܂��ˁc
	�����C�D���ȃ^�C�~���O�ŌĂяo���Ȃ瑽�����r�b�g�ǂݏo���Ă��邩�Ƃ����l���ꏏ�ɕԂ�l�ŕԂ��΂����C�����܂��D	

reset_count()
	���݂̃G���[�r�b�g�������Z�b�g���܂��D

set_measurement_blocks_len(len)
	���u���b�N�ǂݏo���̂��ݒ肵�܂��D
	������64�u���b�N������Ă���̂ŁC64�̔{���ɂȂ�悤�ɐݒ肵�Ă��������D
	


SDCardController
SD�J�[�h��SPI�ʐM�Ő��䂷�邽�߂ɕK�v�ȃ��C�u�����ł��D
micropython��SD�J�[�h���C�u�������x�[�X�ɍ쐬���Ă��܂��D
�C���X�^���X�𐶐�����ɂ�Adafruit_BBIO.SPI�̃C���X�^���X�������ɗ^���Ă��������D
�J�[�h���Ƃɋ������Ⴂ�܂����C����������32GB��SDHC�J�[�h�ł�init_card_v2�CCSD version 2.0���Ăяo����܂����D
SD�J�[�h��1�u���b�N=512�o�C�g�Ȃ̂ŁCread_blocks��write_blocks�̈���buf�ɂ�512�̔{�����̔z���^���Ă��������D

read_blocks(block_num, buf)
	block_num:�w�肵���u���b�N����(buf��/512)�u���b�N���ǂݏo���D
	buf:�ǂݏo���u���b�N�����̔z��
	��:block_num = 0, buf = [0xff] * 512 * 32�̂Ƃ�
	read_blocks��0�u���b�N����31�u���b�N�܂ł�32 * 512�o�C�g���̒l���i�[����buf��Ԃ�l�Ƃ��ĕԂ��D

write_blocks(block_num, buf)
	block_num:�w�肵���u���b�N����(buf��/512)�u���b�N���������ށD
	buf:�������ޒl�Q
	��:block_num = 0, buf = [0xff] * 512 * 32�̂Ƃ�
	read_blocks��0�u���b�N����31�u���b�N�܂ł�buf�z��ɏ���������D

get_sectors()
	���䂵�Ă���r�c�J�[�h�����u���b�N�ō\������Ă��邩�ǂݏo���D
	�Ԃ�l*1024�ōő�u���b�N����������D		

sample
�g�p��������Ă��܂��D

spi-setup
sample�������悤��SPI�s���̐ݒ�����Ă܂��D