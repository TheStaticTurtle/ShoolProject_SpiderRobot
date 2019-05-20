from threading import Thread
from multiprocessing import Process
import time
import Adafruit_PCA9685

def map(x,in_min,in_max,out_min,out_max):
	#See: https://www.arduino.cc/reference/en/language/functions/math/map/#_appendix
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class hook(Process):
	def __init__(self):
		# Thread.__init__(self)
		super(hook, self).__init__()
		self.pwm = Adafruit_PCA9685.PCA9685(address=0x41)
		self.pwm.set_pwm_freq(60)
		self.servo_min = 150  # Min pulse length out of 4096
		self.servo_max = 600  # Max pulse length out of 4096
		self.servosCoxa = [2, 5, 8 ,11]
		self.servosTibia = [1, 4, 7 ,10]
		self.servosFemur = [0, 3, 6 ,9]
		self.action ="stop"

	def set_servo_angle(self,channel, a):
		i = map(a,0,180,150,600)
		self.pwm.set_pwm(channel, 0, i)

	def position_stand_0(self,d):
		for i in self.servosCoxa:
			self.set_servo_angle(i,90)
		for i in self.servosTibia:
			self.set_servo_angle(i,155)
		for i in self.servosFemur:
			self.set_servo_angle(i,90)

	def position_walk_1(self,d):
		self.set_servo_angle(10,180)
		time.sleep(d)
		self.set_servo_angle(11,135)
		time.sleep(d)
		self.set_servo_angle(10,155) 

	def position_walk_2(self,d):
		self.set_servo_angle(2,110)
		self.set_servo_angle(5,135)
		self.set_servo_angle(8,90)
		self.set_servo_angle(11,90)

	def position_walk_3(self,d):
		self.set_servo_angle(4,180)
		time.sleep(d)
		self.set_servo_angle(5,60)
		time.sleep(d)
		self.set_servo_angle(4,155) 

	def position_walk_4(self,d):
		self.set_servo_angle(1,180)
		time.sleep(d)
		self.set_servo_angle(2,50)
		time.sleep(d)
		self.set_servo_angle(1,155) 

	def position_walk_5(self,d):
		self.set_servo_angle(2,90)
		self.set_servo_angle(5,90)
		self.set_servo_angle(8,50)
		self.set_servo_angle(11,50)

	def position_walk_6(self,d):
		self.set_servo_angle(7,180)
		time.sleep(d)
		self.set_servo_angle(8,120)
		time.sleep(d)
		self.set_servo_angle(7,155)

	def run(self):
		self.standIteration = [self.position_stand_0]
		self.forwardIteration = [self.position_walk_1,self.position_walk_2,self.position_walk_3,self.position_walk_4,self.position_walk_5,self.position_walk_6]
		while True:
			if self.action == "stop":
				for act in self.standIteration:
					act(0.5)
					time.sleep(1)
			if self.action == "forward":
				for act in self.forwardIteration:
					act(0.5)
					time.sleep(1)
					if self.action != "forward":
						break
			time.sleep(1)