import spidev
import time
import sys

spi = spidev.SpiDev()
spi.open(0,0)

def analogReadGroove(adcnum):
	if adcnum >7 or adcnum <0:
		return-1
	r = spi.xfer2([1,8+adcnum <<4,0])
	adcout = ((r[1] &3) <<8)+r[2]
	return adcout

while True:
		print ("Channel 0: "),
		value=analogReadGroove(0)
		volts=(value*3.3)/1024
		print("%4d/1023 => %5.3f V" % (value, volts))
		print ("Channel 1: "),
		value=analogReadGroove(1)
		volts=(value*3.3)/1024
		print("%4d/1023 => %5.3f V" % (value, volts))
		print ("Channel 2: "),
		value=analogReadGroove(2)
		volts=(value*3.3)/1024
		print("%4d/1023 => %5.3f V" % (value, volts))
		print ("Channel 3: "),
		value=analogReadGroove(3)
		volts=(value*3.3)/1024
		print("%4d/1023 => %5.3f V" % (value, volts))
		print "_______________________________________\n"
		time.sleep(0.1)
