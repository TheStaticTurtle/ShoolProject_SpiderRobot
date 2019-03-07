"""Simple example showing how to find the device objects."""
from __future__ import division
import pygame
import io
from urllib2 import urlopen
import numpy as np
from threading import Thread
import cv2
import time
import socket
import json
from pynput.keyboard import Key, Listener
import math

pygame.init()
clock = pygame.time.Clock()

class Contoller():
	def __init__(self):
		self.controller = pygame.joystick.Joystick(0)
		self.controller.init()
		self.buttons = []
		self.joystick = []
		pass

	def update(self):
		if self.controller.get_numaxes() == 4:
			self.joystick = [[round(self.controller.get_axis(0),3),round(self.controller.get_axis(1),3)],[round(self.controller.get_axis(2),3),round(self.controller.get_axis(3),3)]]
		elif self.controller.get_numaxes() == 2:
			self.joystick = [[round(self.controller.get_axis(0),3),round(self.controller.get_axis(1),3)],[round(self.controller.get_axis(2),3),round(self.controller.get_axis(3),3)]]
		else:
			print("No analog sticks detected or more than 2")

		self.buttons = []
		for i in range(0,self.controller.get_numbuttons()):
			self.buttons.append(self.controller.get_button(i))

class Contoller_Keyboard():
	def __init__(self):
		self.joystick = [[0,0],[0,0]]
		self.buttons = [0,0,0,0,0,0,0,0,0]
		self.Zkey = False
		self.Qkey = False
		self.Skey = False
		self.Dkey = False
		self.Upkey = False
		self.Downkey = False
		self.Leftkey = False
		self.Rightkey = False
		self.BtnRotCam = False
	
	def constrain(self,x,min,max):
		if x > max:
			x = max
		if x < min:
			x = min
		return x

	def update(self):
	# 	print self.Zkey
	# 	print self.Qkey
	# 	print self.Skey
	# 	print self.Dkey
	# 	print self.Upkey
	# 	print self.Downkey
	# 	print self.Leftkey
	# 	print self.Rightkey
		Ya = 0 
		if self.Zkey:
			Ya +=1
		if self.Skey:
			Ya -=1
		Ya = self.constrain(Ya,-1,1)
		Xa = 0 
		if self.Qkey:
			Xa +=1
		if self.Dkey:
			Xa -=1
		Xa = self.constrain(Xa,-1,1)

		Yb = 0 
		if self.Upkey:
			Yb +=1
		if self.Downkey:
			Yb -=1
		Yb = self.constrain(Yb,-1,1)
		Xb = 0 
		if self.Leftkey:
			Xb +=1
		if self.Rightkey:
			Xb -=1
		Xb = self.constrain(Xb,-1,1)

		self.joystick = [[Xa*-1,Ya*-1],[Xb*-1,Yb*-1]]
		# print self.joystick
		self.buttons = [0,0,0,0,0,0,0,0,0]
		if self.BtnRotCam:
			self.buttons[5] = 1

	def _keydown(self,key):
		key = str(key)
		if key == "u'z'":
			self.Zkey = True
		if key == "u'q'":
			self.Qkey = True
		if key == "u's'":
			self.Skey = True
		if key == "u'd'":
			self.Dkey = True
		if key == "Key.up":
			self.Upkey = True
		if key == "Key.down":
			self.Downkey = True
		if key == "Key.left":
			self.Leftkey = True
		if key == "Key.right":
			self.Rightkey = True
		if key == "u'0'":
			self.BtnRotCam = True

	def _keyup(self,key):
		key = str(key)
		if key == "u'z'":
			self.Zkey = False
		if key == "u'q'":
			self.Qkey = False
		if key == "u's'":
			self.Skey = False
		if key == "u'd'":
			self.Dkey = False
		if key == "Key.up":
			self.Upkey = False
		if key == "Key.down":
			self.Downkey = False
		if key == "Key.left":
			self.Leftkey = False
		if key == "Key.right":
			self.Rightkey = False
		if key == "u'0'":
			self.BtnRotCam = False

class robotController(object):
	"""docstring for robotController"""
	def __init__(self, ip, port):
		super(robotController, self).__init__()
		self.ip = ip
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((ip, port))
		self.livefeedUrl = 0
		self.ping = 0
		self.freeData = "No data recieved yet."
		self.feed = cv2.VideoCapture(self.livefeedUrl)
		self.feedOld = cv2.VideoCapture(self.livefeedUrl)

	def sendJoystickMouvementUpdate(self,x,y):
		x = map(x,0,1024,-1,1)
		y = map(y,0,1024,-1,1)
		if x==0:
			angle = 0
		else:
			angle = math.atan(y/x)
		l=math.sqrt(y**2+x**2)
		sqrt2 = math.sqrt(2)
		l=map(l,0,sqrt2,0,100)
		strenght = l
		angle = math.degrees(angle)

		# angle =  math.degrees(math.atan(y/x));
		if (angle < 0):
			angle += 360;
 
		print((angle,strenght))
		self._send("{\"id\":\"controller\",\"action\":\"joystick\",\"type\":\"mouvement\",\"data\":{\"angle\":"+str(angle)+",\"strenght\":"+str(strenght)+"}}")

	def sendJoystickCameraUpdate(self,x,y):
		x = map(x,0,1024,-1,1)
		y = map(y,0,1024,-1,1)
		if x==0:
			angle = 0
		else:
			angle = math.atan(y/x)
		l=math.sqrt(y**2+x**2)
		sqrt2 = math.sqrt(2)
		l=map(l,0,sqrt2,0,100)
		strenght = 0
		self._send("{\"id\":\"controller\",\"action\":\"joystick\",\"type\":\"camera\",\"data\":{\"angle\":"+str(angle)+",\"strenght\":"+str(strenght)+"}}")

	def requestCurrentLiveFeed(self):
		self._send("{\"id\":\"controller\",\"action\":\"requestlivefeed\"}")

	def getFreeToDisplayMessage(self):
		return self.freedata

	def update(self):
		self._handleData()
		if self.feed != self.feedOld:
			self.feed = cv2.VideoCapture(robot.livefeedUrl)
			self.feedOld = self.feed

	def _send(self,data):
		self.socket.send(data)


	def _handleData(self):
		try:
			data = self.socket.recv(1024)
			if data:
				# print data
				e = data.index("}}") + 2
				data = data[0:e]
				data = ''.join([i if ord(i) < 128 else ' ' for i in data])
				data = data.replace("\n","$$")
				data = data.replace("\r","$$")
				d = json.loads(data)
				if d["action"] == "setlivefeed":
					self.livefeedUrl = d["data"]["url"]
				if d["action"] == "pingcalculation":
					self.ping = int(time.time())-int(int(d["data"]["time"])/1000)
				if d["action"] == "freedata":
					self.freeData = d["data"]["text"]
					self.freeData=self.freeData.replace("$$","\r")
		except Exception as e:
			print e
			

	def getAFrame(self):
		ret_val, img = self.feed.read()
		return img


def updateController():
	for i in range(0,2,1):
		t = []
		for event in pygame.event.get():
			t.append(event)
		controller.update()
		return t

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

controller = Contoller_Keyboard()
keylistener = Listener(on_press=controller._keydown,on_release=controller._keyup)
keylistener.start()

robot = robotController("127.0.0.1",5000)

offsetX_Left=0
offsetY_Left=0
offsetX_Right=0
offsetY_Right=0
textFont = cv2.FONT_HERSHEY_DUPLEX
#textFont = cv2.FONT_HERSHEY_COMPLEX_SMALL
enableControl = True
enableDisplay = True

while True:
	robot.update()
	updateController()

	img = robot.getAFrame()
	if controller.buttons[5] == 1 and controller.buttons[4] == 1:
		enableControl = not enableControl
		time.sleep(.5)

	if enableDisplay:
		cv2.putText(img,'Ping: ',(5,20), textFont,0.5,(255,255,255),2)
		if 0 <= robot.ping <= 200:
			cv2.putText(img,str(robot.ping)+"ms",(50,20), textFont,0.5,(0,255,0),2)
		elif 200 < robot.ping <= 500:
			cv2.putText(img,str(robot.ping)+"ms",(50,20), textFont,0.5,(255,150,0),2)
		elif 500 < robot.ping <= 1000:
			cv2.putText(img,str(robot.ping)+"ms",(50,20), textFont,0.5,(255,0,0),2)

		cv2.putText(img,robot.freeData,(110,20), textFont,0.5,(255,255,255),1)

	if enableControl:
		xLeft = int(img.shape[1] / 6)
		xRight = int(img.shape[1]-img.shape[1] / 6)
		y = int(img.shape[0]-img.shape[0] / 4.5)
		joyradius = 80
		cv2.circle(img, (xLeft,y), joyradius, (255,255,255), 2)
		cv2.circle(img, (xRight,y), joyradius, (255,255,255), 2)

		offsetX_Left = int(map(controller.joystick[0][0],0,1,0,joyradius))
		offsetY_Left = int(map(controller.joystick[0][1],0,1,0,joyradius))

		if controller.buttons[5] == 1:
			offsetX_Right = int(map(controller.joystick[1][0],0,1,0,joyradius))
			offsetY_Right = int(map(controller.joystick[1][1],0,1,0,joyradius))

		cv2.circle(img, (xLeft+offsetX_Left,y+offsetY_Left), 5, (0,255,0), 20)
		cv2.circle(img, (xRight+offsetX_Right,y+offsetY_Right), 5, (0,0,255), 20)

		moveX = int(map(xLeft+offsetX_Left,xLeft-joyradius,xLeft+joyradius,0,1024))
		moveY = int(map(y+offsetY_Left,y-joyradius,y+joyradius,1024,0))

		camX = int(map(xRight+offsetX_Right,xRight-joyradius,xRight+joyradius,0,1024))
		camY = int(map(y+offsetY_Right,y-joyradius,y+joyradius,1024,0))
		robot.sendJoystickMouvementUpdate(moveX,moveY)
		robot.sendJoystickCameraUpdate(camX,camY)
		print([moveX,moveY,camX,camY])
		
	img = cv2.resize(img, (1080, 720))                    # Resize image
	cv2.imshow('Stream', img)
