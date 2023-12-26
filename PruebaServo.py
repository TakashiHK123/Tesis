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

def compuertaAbierta():
    for angleY in range(0,61,5):
        duty_cycley = 2.5 + (angleY/18.0)
        c.ChangeDutyCycle(duty_cycley)
    print("Abierta")
    
def compuertaCerrado():
    for angleA in range(60,-1,-5):
        duty_cycleA = 2.5 +(angleA/18.0)
        c.ChangeDutyCycle(duty_cycleA)#Cuando esta abierto
    print("Cerrado")

def calibrar():
    for angleA in range(61,-1,-5):
        duty_cycleA = 2.5 +(angleA/18.0)
        c.ChangeDutyCycle(duty_cycleA)#Cuando esta abierto
        time.sleep(0.5)
    print("Abierto")
    
def to90grados():
    for angle9 in range(0, 91, 5):
        duty_cycle9 = 2.5 + (angle9 / 18.0)
        p.ChangeDutyCycle(duty_cycle9)
        
        #time.sleep(0.5)
    print("Expulsar")


def to0grados():
    for angle0 in range(100, -1, -5):
        duty_cycle0 = 2.5 + (angle0 / 18.0)
        p.ChangeDutyCycle(duty_cycle0)
        
        #time.sleep(0.5)
    print("Succionar")

try:
    #c.stop()
    #p.stop()
    #GPIO.cleanup()
    #to0grados()
    #time.sleep(2)
    #to90grados()
    #compuertaCerrado()
    #time.sleep(2)
    compuertaAbierta()
    #calibrar()
    #time.sleep(5)
      
except KeyboardInterrupt:
  c.stop()
  GPIO.cleanup()
  print("Cleanup gpio")
