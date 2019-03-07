# -*- coding: utf-8 -*-
import IHM_Hook
# import IHMAudio_Hook
import Sensor_Hook
import ServoSmoother
import time
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',level=logging.DEBUG)
#TEMPORARY
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
camera_setPitchPin = 18
camera_setYawPin = 12
GPIO.setup(camera_setPitchPin, GPIO.OUT)
GPIO.setup(camera_setYawPin, GPIO.OUT)
camera_setPitchPWM = GPIO.PWM(camera_setPitchPin, 100) # GPIO 18 for PWM with 100Hz
camera_setYawPWM = GPIO.PWM(camera_setYawPin, 100) # GPIO 12 for PWM with 100Hz
camera_setPitchPWM.start(2.5) # Initialization
camera_setYawPWM.start(2.5) # Initialization


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

def camera_setPitch(angle):
	camera_setPitchPWM.ChangeDutyCycle((angle/18.0) + 2.5)
	logging.info("setting camera pitch angle: "+str(angle))

def camera_setYaw(angle):
	camera_setYawPWM.ChangeDutyCycle((angle/18.0) + 2.5)
	logging.info("setting camera yaw angle: "+str(angle))

logging.info("Program started")

ihm = IHM_Hook.hook("0.0.0.0",5000)
ihm.start()
# ihmaudio = IHMAudio_Hook.hook("Robot",6980,6981,1,11,verbose=False)
# ihmaudio.start()
ihm.setLiveFeedUrl("http://192.168.1.29:8080/video")

sensors = Sensor_Hook.hook()
sensors.start()

camera_setPitchSmoother = ServoSmoother.Smoother(camera_setPitch)
camera_setYawSmoother = ServoSmoother.Smoother(camera_setYaw)

oldMouv = ""
oldAngle = (0,0)
while True:
	time.sleep(0.01)
	camera_setPitchSmoother.tick()
	camera_setYawSmoother.tick()

	ihm.setFreeText("Distance: "+str(sensors.getDistance())+"cm \nTemperature: "+str(sensors.getTemperature())+"C \nHumidity: "+str(sensors.getHumidity())+"%\nCO2: "+str(sensors.getCO2ppm())+"ppm\nTVOC: "+str(sensors.getTVOCppb())+"ppb")
	logging.debug("Sensors: "+"Distance: "+str(sensors.getDistance())+"cm \t| Temperature: "+str(sensors.getTemperature())+"C \t| Humidity: "+str(sensors.getHumidity())+"%\t| CO2: "+str(sensors.getCO2ppm())+"ppm\t| TVOC: "+str(sensors.getTVOCppb())+"ppb")

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
		camera_setPitchSmoother.goto(ihm.camera_angle[0])
		camera_setYawSmoother.goto(ihm.camera_angle[1])
		oldAngle = ihm.camera_angle