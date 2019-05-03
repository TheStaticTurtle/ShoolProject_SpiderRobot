#-*- coding: utf-8 -*-
from threading import Thread
import IHM_Hook
# import IHMAudio_Hook
import Sensor_Hook
import Servo_Hook
import ServoSmoother
import time
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',level=logging.DEBUG)

def walk_forward():
	logging.info("Turing the robot forward")

def walk_backward():
	logging.info("Turing the robot backward")

def walk_right():
	logging.info("Turing the robot right")

def walk_left():
	logging.info("Turing the robot left")

def turn_toright():
	logging.info("Turing the robot right")

def turn_toleft():
	logging.info("Turing the robot left")

def stop():
	logging.info("Stop moving the robot left")

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

# class servoSmootherTicker(Thread):
#     def __init__(self):
#         Thread.__init__(self)
#         self.running = True

#     def run(self):
#         while self.running:
# 		time.sleep(0.005)
# 		camera_setPitchSmoother.tick()
# 		camera_setYawSmoother.tick()

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

servos = Servo_Hook.hook()
servos.start()

tickerIHMUpdater = ticker(0.5,updateIHM)
tickerIHMUpdater.start()

logging.info("Classes started wating for a bit")
time.sleep(1)

servos.setServoPulse(12, 90)
servos.setServoPulse(13, 90)

oldMouv = ""
oldAngle = (0,0)
while True:
	time.sleep(0.01)
	logging.debug("Sensors: "+"Distance: "+str(sensors.getDistance())+"cm \t| Temperature: "+str(sensors.getTemperature())+"C \t| Humidity: "+str(sensors.getHumidity())+"%\t| CO2: "+str(sensors.getCOppm())+"ppm\t| Pollution: "+sensors.getAirQuality())

	if ihm.walkmode != oldMouv:
		if ihm.walkmode == "forward":
			walk_forward()
		elif ihm.walkmode == "backward":
			walk_backward()
		elif ihm.walkmode == "right":
			walk_right()
		elif ihm.walkmode == "left":
			walk_left()
		elif ihm.walkmode == "turnleft":
			turn_toleft()
		elif ihm.walkmode == "turnright":
			turn_toright()
		else:
			stop()
		oldMouv = ihm.walkmode
		
	if ihm.camera_angle != oldAngle:
		logging.warning(ihm.camera_angle[0])
		logging.warning(ihm.camera_angle[1])
		servos.setServoPulse(12, ihm.camera_angle[0] )
		servos.setServoPulse(13, ihm.camera_angle[1] )
		oldAngle = ihm.camera_angle
