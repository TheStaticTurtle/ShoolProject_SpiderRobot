# -*- coding: utf-8 -*-
import IHM_Hook
from random import randint
import time

def walk_forward():
	print("Walking forward")

def walk_backward():
	print("Walking backward")

def walk_right():
	print("Walking right")

def walk_left():
	print("Walking left")

def turn_toright():
	print("Turning right")

def turn_toleft():
	print("Turning left")

def stop():
	print("Stoppted")

def camera_setPitch(angle):
	print("Camera pitch angle: "+str(angle))

def camera_setYaw(angle):
	print("Camera yaw angle: "+str(angle))

cameraFunction = (camera_setPitch,camera_setYaw)
ihm = IHM_Hook.hook("0.0.0.0",5000,cameraFunction)
ihm.start()
ihm.setLiveFeedUrl("http://192.168.1.29:8080/video")


oldMouv = ""
oldAngle = (0,0)
while True:
	time.sleep(1)
	ihm.setFreeText("Distance: "+str(randint(1, 15))+"cm\nTemperature: "+str(randint(-10, 60))+"°")
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
		camera_setPitch(ihm.camera_angle[0])
		camera_setYaw(ihm.camera_angle[1])
		oldAngle = ihm.camera_angle