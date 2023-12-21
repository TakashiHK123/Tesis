import RPi.GPIO as GPIO
import time

servoCompuertaPIN = 6
servoSelectorPIN = 13
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoCompuertaPIN, GPIO.OUT)
GPIO.setup(servoSelectorPIN, GPIO.OUT)
c = GPIO.PWM(servoCompuertaPIN, 50) # GPIO 17 for PWM with 50Hz
c.start(2.5)

p = GPIO.PWM(servoSelectorPIN,50)
p.start(2.5)

def compuertaCerrado():
    for angleY in range(0,60,60):
        duty_cycley = 2.5 + (angleY/18.0)
        c.ChangeDutyCycle(duty_cycley)
        time.sleep(0.5)
    print("Cerrado")
    
def compuetaAbierta():
    for angleA in range(60,-1,-60):
        duty_cycleA = 2.5 +(angleA/18.0)
        c.ChangeDutyCycle(duty_cycleA)#Cuando esta abierto
        time.sleep(0.5)
    print("Abierto")

def calibrar():
    for angleA in range(60,-1,-60):
        duty_cycleA = 2.5 +(angleA/18.0)
        c.ChangeDutyCycle(duty_cycleA)#Cuando esta abierto
        time.sleep(0.5)
    print("Abierto")

try:
    #compuertaCerrado()
    #time.sleep(2)
    #compuetaAbierta()
    #calibrar()
    #time.sleep(5)
      
except KeyboardInterrupt:
  c.stop()
  GPIO.cleanup()
  print("Cleanup gpio")
