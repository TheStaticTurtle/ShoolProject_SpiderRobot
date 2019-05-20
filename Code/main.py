#-*- coding: utf-8 -*-
from threading import Thread
import IHM_Hook
# import IHMAudio_Hook
import Sensor_Hook
# import Servo_Hook
import ServoSmoother
import time
import logging
from multiprocessing import Process
import Adafruit_PCA9685

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',level=logging.DEBUG)

# def walk_forward():
# 	logging.info("Turing the robot forward")

# def walk_backward():
# 	logging.info("Turing the robot backward")

# def walk_right():
# 	logging.info("Turing the robot right")

# def walk_left():
# 	logging.info("Turing the robot left")

# def turn_toright():
# 	logging.info("Turing the robot right")

# def turn_toleft():
# 	logging.info("Turing the robot left")

# def stop():
# 	logging.info("Stop moving the robot left")

# def camera_setPitch(ang):
# 	d = float(ang)/10.+5.
# 	#camera_setPitchPWM.ChangeDutyCycle(d)
# 	logging.info("setting camera pitch angle: "+str(ang))

# def camera_setYaw(ang):
# 	ang = 180 - ang
# 	d = float(ang)/10.+5.
# 	#camera_setYawPWM.ChangeDutyCycle(d)
# 	logging.info("setting camera yaw angle: "+str(ang))

def updateIHM():
	ihm.setFreeText("Distance: "+str(sensors.getDistance())+"cm \nTemperature: "+str(sensors.getTemperature())+"C \nHumidity: "+str(sensors.getHumidity())+"%\n CO: "+str(sensors.getCOppm())+"ppm \nPollution: "+sensors.getAirQuality())
	time.sleep(0.1)
	ihm.sendKeepAlive()

def map(x,in_min,in_max,out_min,out_max):
	#See: https://www.arduino.cc/reference/en/language/functions/math/map/#_appendix
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# class servoSmootherTicker(Thread):
#     def __init__(self):
#         Thread.__init__(self)
#         self.running = True

#     def run(self):
#         while self.running:
# 		time.sleep(0.005)
# 		camera_setPitchSmoother.tick()
# 		camera_setYawSmoother.tick()


class servs(object):
	def __init__(self):
		# Thread.__init__(self)
		super(servs, self).__init__()
		self.pwm = Adafruit_PCA9685.PCA9685(address=0x41)
		self.pwm.set_pwm_freq(60)
		self.servo_min = 150  # Min pulse length out of 4096
		self.servo_max = 600  # Max pulse length out of 4096
		self.servosCoxa = [2, 5, 8 ,11]
		self.servosTibia = [1, 4, 7 ,10]
		self.servosFemur = [0, 3, 6 ,9]
		self.action ="stop"
		self.standIteration = []
		self.forwardIteration = []
		self.step = 0
		
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

	def init(self):
		self.standIteration = [self.position_stand_0]
		self.forwardIteration = [self.position_walk_1,self.position_walk_2,self.position_walk_3,self.position_walk_4,self.position_walk_5,self.position_walk_6]
		self.step = 0

	def tick(self):
		if self.action == "stop":
			self.step = 0
			act = self.standIteration[self.step]
		if self.action == "forward":
			act = self.standIteration[self.step]
			self.step += 1
			time.sleep(1)
			if self.step == len(self.standIteration):
				self.step = 0

class ticker(Thread):
    def __init__(self,delay,callback):
        Thread.__init__(self)
        self.running = True
	self.delay = delay
	self.callback = callback

    def run(self):
        while self.running:
		time.sleep(self.delay)
		self.callback()


logging.info("Program started")

ihm = IHM_Hook.hook("0.0.0.0",5000)
ihm.start()
# ihmaudio = IHMAudio_Hook.hook("Robot",6980,6981,1,11,verbose=False)
# ihmaudio.start()
ihm.setLiveFeedUrl("http://192.168.4.1:9000/?action=video")

sensors = Sensor_Hook.hook()
sensors.start()

servos = servs()
servos.init()

tickerIHMUpdater = ticker(0.5,updateIHM)
tickerIHMUpdater.start()

logging.info("Classes started wating for a bit")
time.sleep(1)

servos.set_servo_angle(12, 90)
servos.set_servo_angle(13, 90)

def main():
	oldMouv = ""
	oldAngle = (0,0)
	while True:
		servos.action = ihm.walkmode
		servos.tick()

		time.sleep(0.01)
		logging.debug("Sensors: "+"Distance: "+str(sensors.getDistance())+"cm \t| Temperature: "+str(sensors.getTemperature())+"C \t| Humidity: "+str(sensors.getHumidity())+"%\t| CO2: "+str(sensors.getCOppm())+"ppm\t| Pollution: "+sensors.getAirQuality())

		if ihm.camera_angle != oldAngle:
			logging.warning(ihm.camera_angle[0])
			logging.warning(ihm.camera_angle[1])
			servos.set_servo_angle(12, ihm.camera_angle[0] )
			servos.set_servo_angle(13, ihm.camera_angle[1] )
			oldAngle = ihm.camera_angle

main()
# p = Thraead(target=main)
# p.start()
# p.join()





