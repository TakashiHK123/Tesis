import RPi.GPIO as GPIO
import time

servoPIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5)
try:
  while True:
      
    for angleY in range(0,60,60):
        duty_cycle = 2.5 + (angleY/18.0)
        p.ChangeDutyCycle(duty_cycle)
        print("Compuerta Cerrado")
        time.sleep(1)
    for angle in range(60,-1,-60):
        duty_cycle = 2.5 +(angle/18.0)
        p.ChangeDutyCycle(duty_cycle)#Cuando esta abierto
        print("Compuerta Abierto")
        time.sleep(5)
        
except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()
  print("Cleanup gpio")
