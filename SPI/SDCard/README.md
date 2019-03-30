Control of the SD card using the SPI.

XRayDetector(SDCardController)
SDカードを使ってビット反転を検出するために開発したライブラリです．
SDCardControllerを継承しています．
インスタンスの生成方法はSDCardControllerに同じです．

start_measurement()
	SDカードが何ビット反転しているか計測する非同期処理を開始します．
	1ループあたり64ブロック読み出して，読み出したビット列を全て1に戻す処理が行われています．
	32GBを全て計測するには120時間程度かかると思われます．	

stop_measurement()
	start_measurement()で開始した非同期処理を終了します．
	呼び出してから現在読み出しているブロック長分読み終わってから，残りのブロック長に関わらず終了します．
	処理が終わっていることが明白でもスレッドをjoinしている場所なので必ず呼び出してあげてください．

get_count()
	現在のエラービット数を返します．
	計測が終了してから呼び出さないと意味ない気がしますね…
	もし，好きなタイミングで呼び出すなら多分何ビット読み出しているかという値も一緒に返り値で返せばいい気がします．	

reset_count()
	現在のエラービット数をリセットします．

set_measurement_blocks_len(len)
	何ブロック読み出すのか設定します．
	処理を64ブロックずつやっているので，64の倍数になるように設定してください．
	


SDCardController
SDカードをSPI通信で制御するために必要なライブラリです．
micropythonのSDカードライブラリをベースに作成しています．
インスタンスを生成するにはAdafruit_BBIO.SPIのインスタンスを引数に与えてください．
カードごとに挙動が違いますが，私が試した32GBのSDHCカードではinit_card_v2，CSD version 2.0が呼び出されました．
SDカードは1ブロック=512バイトなので，read_blocksやwrite_blocksの引数bufには512の倍数長の配列を与えてください．

read_blocks(block_num, buf)
	block_num:指定したブロックから(buf長/512)ブロック分読み出す．
	buf:読み出すブロック長分の配列
	例:block_num = 0, buf = [0xff] * 512 * 32のとき
	read_blocksは0ブロックから31ブロックまでの32 * 512バイト分の値を格納したbufを返り値として返す．

write_blocks(block_num, buf)
	block_num:指定したブロックから(buf長/512)ブロック分書き込む．
	buf:書き込む値群
	例:block_num = 0, buf = [0xff] * 512 * 32のとき
	read_blocksは0ブロックから31ブロックまでをbuf配列に書き換える．

get_sectors()
	制御しているＳＤカードが何ブロックで構成されているか読み出す．
	返り値*1024で最大ブロック長が分かる．		
	
sample
使用例を挙げています．

spi-setup
sampleが動くようにSPIピンの設定をしてます．