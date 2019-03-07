from threading import Thread
import time
import pyaudio
import socket 
import struct
def getDevices():
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')

	print "--- INPUT DEVICES ---"
	for i in range(0, numdevices):
		if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
			print "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'), " - ",p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')
			
	print "--- OUTPUT DEVICES ---"
	for i in range(0, numdevices):
		if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
			print "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'), " - ",p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')

class hook(Thread):
	def __init__(self,streamName,inPort,outPort,inDevice,outDevice,verbose=False):
		Thread.__init__(self)
		self.sockin = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		self.sockin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sockin.bind(("0.0.0.0", inPort))
		self.sockin_port  = inPort
		self.sockout = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockout.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sockout.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.sockout_port = outPort

		self.vban_streamName  = streamName
		self.vban_sampRateLst = [6000, 12000, 24000, 48000, 96000, 192000, 384000, 8000, 16000, 32000, 64000, 128000, 256000, 512000,11025, 22050, 44100, 88200, 176400, 352800, 705600]
		self.vban_out_frameCounter = 0
		self.audio_sampleRate = 48000
		self.audio_channels   = 1
		self.audio_chunkSize  = 256
		self.audio_outDeviceIndex = outDevice
		self.audio_inDeviceIndex = inDevice

		self.p = pyaudio.PyAudio()
		self.audioStream = self.p.open(
			format   = self.p.get_format_from_width(2),
			rate     = self.audio_sampleRate,
			output   = True,
			input    = True,
			output_device_index = self.audio_outDeviceIndex,
			input_device_index  = self.audio_inDeviceIndex,
			channels = self.audio_channels
		)

		self.rawPcm  = None
		self.rawData = None
		self.running = True
		self.verbose = verbose

	def _cutAtNullByte(self,stri):
		return stri.split("\x00")[0]

	def run(self):
		while self.running:
			if self.audioStream == None:
				print("stream==None : Quit has been called")
				return

			data, addr = self.sockin.recvfrom(2048) # buffer size is normally 1436 bytes Max size for vban

			magicString = data[0:4]
			subprotocol = (ord(data[4]) & 0xE0) >> 5
			sampRate = self.vban_sampRateLst[ord(data[4]) & 0x1F]
			sampNum = ord(data[5]) + 1
			chanNum = ord(data[6]) + 1
			dataFormat = ord(data[7])
			streamName = self._cutAtNullByte(''.join(struct.unpack("cccccccccccccccc",data[8:24])))
			frameCounter = struct.unpack("l",data[24:28])[0]
			self.rawData = data
			self.rawPcm = data[28:]   #Header stops a 28

			print "R"+magicString+" Name:"+streamName+" Frame:"+str(frameCounter) +" DATALEN:"+str(len(data[28:]))

			if magicString == "VBAN":
				if streamName == self.vban_streamName:
					try:
						self.audioStream.write(self.rawPcm)
					except Exception as e:
							print e
							self.audioStream = self.p.open(
								format   = pyaudio.paInt16,#self.p.get_format_from_width(2),
								rate     = self.audio_sampleRate,
								output   = True,
								input    = True,
								output_device_index = self.audio_outDeviceIndex,
								input_device_index  = self.audio_inDeviceIndex,
								channels = self.audio_channels
							)

			#Transmitt audio
			self.vban_out_frameCounter += 1
			header  = "VBAN" 
			header += chr(self.vban_sampRateLst.index(self.audio_sampleRate))
			header += chr(255) #Chunk size
			header += chr(self.audio_channels)
			header += chr(1)  #VBAN_CODEC_PCM
			header += self.vban_streamName + "\x00" * (16 - len(self.vban_streamName))
			header += struct.pack("l",self.vban_out_frameCounter)
			
			print "SVBAN Name:"+self.vban_streamName+" Frame:"+str(self.vban_out_frameCounter)

			try:
				data = header + self.audioStream.read(256)
				self.sockout.sendto(data, ('192.168.1.255', self.sockout_port))
			except Exception as e:
				print e
				self.audioStream = self.p.open(
					format   = self.p.get_format_from_width(2),
					rate     = self.audio_sampleRate,
					output   = True,
					input    = True,
					output_device_index = self.audio_outDeviceIndex,
					input_device_index  = self.audio_inDeviceIndex,
					channels = self.audio_channels
				)
			

			




getDevices()
# t = hook("Robot",6980,6981,1,11,verbose=True)
# t.start()
# while True:
# 	pass
# vban_receptor -i 192.168.1.11 -p 6980 -s Robot -b alsa -o hw:CARD=Device,DEV=0