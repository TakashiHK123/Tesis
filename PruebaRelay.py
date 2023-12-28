import RPi.GPIO as GPIO
import time

# Configura el modo de la GPIO
GPIO.setmode(GPIO.BCM)

# Define el número del pin GPIO que deseas usar
pinSuccionador = 16

# Configura el pin como entrada
GPIO.setup(pinSuccionador, GPIO.OUT)

GPIO.output(pinSuccionador, GPIO.LOW)
print('HIGH')
time.sleep(2)
GPIO.output(pinSuccionador, GPIO.HIGH)
print('LOW')
time.sleep(2)