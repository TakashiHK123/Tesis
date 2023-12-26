import RPi.GPIO as GPIO
import time

servoCompuertaPIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoCompuertaPIN, GPIO.OUT)

c = GPIO.PWM(servoCompuertaPIN, 50) # GPIO 17 for PWM with 50Hz
c.start(2.5)
try:
  while True:

    for angleY in range(0,60,60):
        duty_cycle = 2.5 + (angleY/18.0)
        c.ChangeDutyCycle(duty_cycle)
        print("Compuerta Cerrado")
        time.sleep(1)
    for angle in range(60,-1,-60):
        duty_cycle = 2.5 +(angle/18.0)
        c.ChangeDutyCycle(duty_cycle)#Cuando esta abierto
        print("Compuerta Abierto")
        time.sleep(5)

except KeyboardInterrupt:
  c.stop()
  GPIO.cleanup()
  print("Cleanup gpio")
