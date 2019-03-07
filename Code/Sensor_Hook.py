import Adafruit_DHT
import RPi.GPIO as GPIO
from threading import Thread
import time
import smbus

class hook(Thread):
	def __init__(self):
		Thread.__init__(self)
		GPIO.setmode(GPIO.BCM)
		self.DHT11_pin = 4
		self.DHT11_temerature = 0
		self.DHT11_humidity = 0
		self.SR04_1_pin_trig = 23
		self.SR04_1_pin_echo = 24
		self.SR04_1_distance = 0
		self.SR04_1_timeout  = 1
		self.i2cbus             = smbus.SMBus(1)
		self.iAQCore_bufferSize = 8
		self.iAQCore_address    = 0x08
		self.iAQCore_co2ppm     = -1
		self.iAQCore_status     = -1
		self.iAQCore_resistance = -1
		self.iAQCore_tvocppb    = -1

	def setup(self):
		GPIO.setwarnings(False)
		GPIO.setup(self.SR04_1_pin_trig,GPIO.OUT)
		GPIO.setup(self.SR04_1_pin_echo,GPIO.IN)

	def update_iAQCore(self):
		try:
			buf = self.i2cbus.read_i2c_block_data(self.iAQCore_address,self.iAQCore_bufferSize)
			self.iAQCore_status =  buf[2]
			if(self.iAQCore_status == 0x00):
				self.iAQCore_co2ppm     =  (buf[0]<<8) + (buf[1]<<0)
				self.iAQCore_resistance =  (buf[3]<<24) + (buf[4]<<16) + (buf[5]<<8) + (buf[6]<<0)
				self.iAQCore_tvocppb    =  (buf[7]<<8) + (buf[8]<<0)
			elif(self.iAQCore_status == 0x10):
				print("WARNING: Can't get mesurment of iAQCore (Still warming up)")
			elif(self.iAQCore_status == 0x01):
				print("WARNING: Can't get mesurment of iAQCore (BUSY)")
			elif(self.iAQCore_status == 0x80):
				print("ERROR  : Can't get mesurment of iAQCore (ERROR)")
		except IOError as e:
			print("ERROR  : Can't get mesurment of iAQCore ("+str(e)+")")


	def update_DHT11(self):
		self.DHT11_humidity , self.DHT11_temerature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.DHT11_pin)

	def update_SR04_1(self):
		GPIO.output(self.SR04_1_pin_trig, True)
		time.sleep(0.00001)
		GPIO.output(self.SR04_1_pin_trig, False) #Launch trigger

		echoStart = 0
		echoEnd = 0
		timeout = time.time()

		while GPIO.input(self.SR04_1_pin_echo)==0:
			echoStart = time.time()	#Waits for the echo start
			if time.time() > timeout + self.SR04_1_timeout*2:
				print("WARNING: Timeout while reading echoStart of SR04_1")
				echoStart = 0
				echoEnd = -(1/17000) #Bit of math to get 0 when timeout
				break

		while GPIO.input(self.SR04_1_pin_echo)==1:
			echoEnd = time.time()		#Waits for the echo stop
			if time.time() > echoStart + self.SR04_1_timeout:
				print("WARNING: Timeout while reading echoEnd of SR04_1")
				echoStart = 0
				echoEnd = -(1/17000) #Bit of math to get 0 when timeout
				break

		self.SR04_1_distance = round((echoEnd - echoStart) * 340 * 100 / 2, 1)  ## Speed of sound = 340 m/s

	def getDistance(self):
		return self.SR04_1_distance
	def getTemperature(self):
		return self.DHT11_temerature
	def getHumidity(self):
		return self.DHT11_humidity
	def getCO2ppm(self):
		return self.iAQCore_co2ppm
	def getTVOCppb(self):
		return self.iAQCore_tvocppb

	def run(self):
		self.setup()
		while True:
			self.update_DHT11()
			self.update_SR04_1()
			self.update_iAQCore()