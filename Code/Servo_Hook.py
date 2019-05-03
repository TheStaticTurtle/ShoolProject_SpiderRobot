from threading import Thread
import time
import Adafruit_PCA9685

def map(x,in_min,in_max,out_min,out_max):
	#See: https://www.arduino.cc/reference/en/language/functions/math/map/#_appendix
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class hook(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.pwm = Adafruit_PCA9685.PCA9685(address=0x41)
		self.pwm.set_pwm_freq(60)
		self.servo_min = 150  # Min pulse length out of 4096
		self.servo_max = 600  # Max pulse length out of 4096

	def setServoPulse(self,channel,angle):
		pulse = map(angle,0,180,self.servo_min,self.servo_max)
		self.pwm.set_pwm(channel, 0, pulse)

	def run(self):
		while True:
			time.sleep(1)
