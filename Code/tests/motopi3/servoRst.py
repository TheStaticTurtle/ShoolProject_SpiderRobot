import Adafruit_PCA9685
import time
pwm = Adafruit_PCA9685.PCA9685(address=0x41)

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
def map(x,in_min,in_max,out_min,out_max):
	#See: https://www.arduino.cc/reference/en/language/functions/math/map/#_appendix
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

#chan = 12

servosCoxa = [2, 5, 8 ,11]
servosTibia = [1, 4, 7 ,10]
servosFemur = [0, 3, 6 ,9]

for chan in range(0,12):
	j = 90
	i = map(j,0,180,150,600)
	pwm.set_pwm(chan, 0, i)

while True:
	j = input("angle: ")
	for chan in servosTibia:
		i = map(j,0,180,150,600)
		pwm.set_pwm(chan, 0, i)
