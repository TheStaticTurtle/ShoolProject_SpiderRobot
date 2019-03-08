import random
import sys
import threading
import time
import json
import socket 
import math
import traceback

class ClientThread(threading.Thread):
	def __init__(self, ip, port, clientsocket, hookThread):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsocket = clientsocket
		self.running=True
		self.clientsocket.setblocking(1)
		self.hookThread = hookThread
		self.lastsend = time.time()

	def run(self): 
		print("[+] Connexion de %s %s" % (self.ip, self.port, ))
		while self.running:
			try:
				response = self.clientsocket.recv(9999)
				if response != "":
					print response[:-1]
					self.hookThread.addDataToQueue(response)
			except Exception,e:
				print e

		print("[-] Deconnexion de %s %s" % (self.ip, self.port, ))

	def send(self,msg):
		if self.lastsend + 0.050 < time.time():
			try:
				if self.clientsocket != None:
					self.clientsocket.send(msg)
			except Exception,e:
				self.close()
				self.running=False
				print e
		

	def close(self):
		self.running=False
		try:
			self.clientsocket.close()
		except:
			pass
		self.clientsocket = None

class ClientListenner(threading.Thread):
	def __init__(self,port,hookThread):
		threading.Thread.__init__(self)
		self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.tcpsock.bind(("",port))
		self.running=True
		self.clientList = []
		self.hookThread = hookThread
		print("[+] En ecoute...")

	def run(self):
		while self.running:
			try:
				self.tcpsock.listen(1)
				self.tcpsock.settimeout(3)
				(clientsocket, (ip, port)) = self.tcpsock.accept()
				newthread = ClientThread(ip, port, clientsocket, self.hookThread)
				newthread.start()
				self.clientList.append(newthread)
			except socket.timeout:
				pass
			except Exception as e:
				raise e

	def stop(self):
		self.tcpsock.close()
		self.tcpsock = None
		self.running = False


def map(x,in_min,in_max,out_min,out_max):
	#See: https://www.arduino.cc/reference/en/language/functions/math/map/#_appendix
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class hook(threading.Thread):
	def __init__(self, bindip, bindport):
		threading.Thread.__init__(self)
		self.bindip = bindip
		self.bindport = bindport
		self.minJoystickStrenght = 50
		self.walkmode = "stop"
		self.running = True
		self.listenner = ClientListenner(bindport,self)
		self.listenner.hookThread = self
		self.dataQueue = []
		self.walkJoystickPosition = (0,0)
		self.cameraJoystickPosition = (0,0)
		self.liveFeedUrl = "file:///android_res/raw/nofeed.html"
		self.camera_angle_maxY = 90+45
		self.camera_angle_minY = 90-45
		self.camera_angle_maxX = 90+50
		self.camera_angle_minX = 90-50
		self.camera_angle = (self.camera_angle_minX,self.camera_angle_minY)

	def addDataToQueue(self,data):
		self.dataQueue.append(data)

	def prosessQueue(self):
		for item in self.dataQueue:
			try:
				item = json.loads(item)
				if item["action"] == "joystick":
					if item["id"] == "controller" and item["type"] == "mouvement":
						self.walkJoystickPosition = (item["data"]["angle"] ,item["data"]["strenght"])
					if item["id"] == "controller" and item["type"] == "camera":
						self.cameraJoystickPosition = (item["data"]["angle"] ,item["data"]["strenght"])
				if item["action"] == "requestlivefeed":
					self.setLiveFeedUrl(self.liveFeedUrl)

			except Exception as e:
				traceback.print_exc()
				print item
		self.dataQueue = []

	def calculateMovingAction(self,angle,strengh):
		#Joystick 45 To 135 Up
		#Joystick 135 To 225 Left
		#Joystick 225 To 315 Down
		#Joystick 315 To 45 Right
		if 45 < angle and angle < 135:
			if strengh>self.minJoystickStrenght:
				self.walkmode = "forward"
		if 135 <= angle and angle <= 225:
			if strengh>self.minJoystickStrenght:
				self.walkmode = "left"
		if 255 <= angle and angle <= 315:
			if strengh>self.minJoystickStrenght:
				self.walkmode = "backward"
		if (angle >= 315 and angle <= 360) or (angle >= 0 and angle <= 45):
			if strengh>self.minJoystickStrenght:
				self.walkmode = "right"
		if strengh<self.minJoystickStrenght:
				self.walkmode = "stop"

	def calculateCameraAction(self,angle,strenght):
		if strenght == 0: #Avoid divde by 0
			self.camera_angle = (self.camera_angle_maxX / 2, self.camera_angle_maxY/2)
			return

		x = math.cos( math.radians(angle) ) * strenght
		y = math.sin( math.radians(angle) ) * strenght
		# Here result goes from -100 to 100 So let's map it to the camera angle
		x = int(map(x,-100,100,self.camera_angle_minX,self.camera_angle_maxX))
		y = int(map(y,-100,100,self.camera_angle_minY,self.camera_angle_maxY))
		self.camera_angle = (x,y)

	def calculateCameraAction(self,angle,strenght):
		#See: https://stackoverflow.com/questions/24917804/how-to-translate-joystick-angle-power-to-the-view-x-y-i-want-to-move/24927983
		x = math.cos( math.radians(angle) );
		y = math.sin( math.radians(angle) );
		length = math.sqrt( (x*x) + (y*y) );
		x /= length;
		y /= length;
		# Here result goes from -1 to 1 So let's map it
		x = int(map(x,-1,1,self.camera_angle_minX,self.camera_angle_maxX))
		y = int(map(y,-1,1,self.camera_angle_minY,self.camera_angle_maxY))
		self.camera_angle = (x,y)

	def setLiveFeedUrl(self,url):
		self.liveFeedUrl = url
		for c in self.listenner.clientList:
			c.send("{\"action\":\"setlivefeed\",\"data\":{\"url\":\""+url+"\"}}")

	def setFreeText(self,text):
		for c in self.listenner.clientList:
			c.send("{\"action\":\"freedata\",\"data\":{\"text\":\""+text+"\"}}")

	def sendKeepAlive(self):
		t = str(int(round(time.time() * 1000)))
		for c in self.listenner.clientList:
			c.send("{\"action\":\"pingcalculation\",\"data\":{\"time\":\""+t+"\"}}")

	def stop(self):
		self.running = False
		for c in self.listenner.clientList:
			c.close()
		self.listenner.stop()

	def run(self):
		self.listenner.start()

		while self.running:
			self.prosessQueue()
			self.calculateMovingAction(self.walkJoystickPosition[0],self.walkJoystickPosition[1])
			self.calculateCameraAction(self.cameraJoystickPosition[0],self.cameraJoystickPosition[1])



