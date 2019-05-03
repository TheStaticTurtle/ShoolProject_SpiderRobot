import Adafruit_DHT
import RPi.GPIO as GPIO
from threading import Thread
import time
import spidev

class hook(Thread):
	def __init__(self):
		Thread.__init__(self)
		GPIO.setmode(GPIO.BCM)
		self.DHT22_pin = 4
		self.DHT22_temerature = 0
		self.DHT22_humidity = 0
		self.SR04_1_pin_trig = 24
		self.SR04_1_pin_echo = 23
		self.SR04_1_distance = 0
		self.SR04_1_timeout  = 1
		self.MQ9_COppm = 0
		self.spi = spidev.SpiDev()
		self.spi.open(0,0)
		self.AirQuality_normalized = ""
		self.AirQuality_raw = 0
		self.AirQuality_standart = 0
		self.AirQuality_standart_sum = 0
		self.AirQuality_standart_iteration = 0
		self.AirQuality_standart_lastupdate = 0

	def setup(self):
		GPIO.setwarnings(False)
		GPIO.setup(self.SR04_1_pin_trig,GPIO.OUT)
		GPIO.setup(self.SR04_1_pin_echo,GPIO.IN)

	def motoPi3_analogRead(self,adcnum):
		if adcnum >7 or adcnum <0:
			return-1
		r = self.spi.xfer2([1,8+adcnum <<4,0])
		adcout = ((r[1] &3) <<8)+r[2]
		return adcout

	def MQ9_VoltageToPPM(self,v):
		try:
			VIN = 3.3 # Volts
			ANALOG_MAX = 1024 #
			Ro = 15000 # BOard resistor
	
			Vrl = v * ( VIN / ANALOG_MAX  )
			Rs = 20000 * ( VIN - Vrl) / Vrl #Ohms law
			ratio =  Rs/Ro #Co ratio
	
			ppm = 37143 * ( ratio**-3.178 )
			return ppm
		except:
			return 0

	def calculateAirQuality(self,analog):
		old = self.AirQuality_raw
		self.AirQuality_raw = analog

		self.AirQuality_standart_sum += self.AirQuality_raw
		self.AirQuality_standart_iteration += 1

		if(time.time() > self.AirQuality_standart_lastupdate + 500):
			self.AirQuality_standart = self.AirQuality_standart_sum / self.AirQuality_standart_iteration
			self.AirQuality_standart_lastupdate = time.time()

		if (self.AirQuality_raw - old > 400 or self.AirQuality_raw > 700):
			return "Forte"
		elif ((self.AirQuality_raw - old > 400 and self.AirQuality_raw < 700) or self.AirQuality_raw - self.AirQuality_standart > 150):
			return "Haute"
		elif ((self.AirQuality_raw - old > 200 and self.AirQuality_raw < 700) or self.AirQuality_raw - self.AirQuality_standart > 50):
			return "Basse"
		else:
			return "Aucune"
		return "Erreur"

	def update_MotoPi(self):
		# channel1 = self.motoPi3_analogRead(0)
		channel2 = self.motoPi3_analogRead(1)
		channel3 = self.motoPi3_analogRead(2)
		# channel4 = self.motoPi3_analogRead(3)
		
		self.MQ9_COppm = self.MQ9_VoltageToPPM(channel3)
		self.AirQuality_normalized = self.calculateAirQuality(channel2)

	def update_DHT22(self):
		self.DHT22_humidity , self.DHT22_temerature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.DHT22_pin)

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
		return round(self.DHT22_temerature,5)
	def getHumidity(self):
		return round(self.DHT22_humidity,5)
	def getCOppm(self):
		return round(self.MQ9_COppm,5)
	def getAirQuality(self):
		return self.AirQuality_normalized

	def run(self):
		self.setup()
		while True:
			self.update_DHT22()
			self.update_SR04_1()
			self.update_MotoPi()
