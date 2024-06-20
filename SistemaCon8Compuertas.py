
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# libraries
import time
import RPi.GPIO as GPIO
# Use BCM GPIO references
# Instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
# Define GPIO signals to use Pins 18,22,24,26 GPIO24,GPIO25,GPIO8,GPIO7
StepPins = [17,18,27,22]
# Set all pins as output

#Definir fan de succion y de empuje
servoPIN = 13
#succionFan = 6
#empujeFan = 5
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(succionFan, GPIO.OUT)
# GPIO.setup(empujeFan, GPIO.OUT)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
p = GPIO.PWM(servoPIN, 50) # GPIO 13 for PWM with 50Hz
p.start(2.5) 
for pin in StepPins:
        print("Setup pins")
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin, False)
# Define some settings
WaitTime = 0.005
# Define simple sequence
StepCount1 = 4
Seq1 = []
Seq1 = [i for i in range(0, StepCount1)]
Seq1[0] = [1,0,0,0]
Seq1[1] = [0,1,0,0]
Seq1[2] = [0,0,1,0]
Seq1[3] = [0,0,0,1]
# Define advanced half-step sequence
StepCount2 = 8
Seq2 = []
Seq2 = [i for i in range(0, StepCount2)]
Seq2[0] = [1,0,0,0]
Seq2[1] = [1,1,0,0]
Seq2[2] = [0,1,0,0]
Seq2[3] = [0,1,1,0]
Seq2[4] = [0,0,1,0]
Seq2[5] = [0,0,1,1]
Seq2[6] = [0,0,0,1]
Seq2[7] = [1,0,0,1]
# Choose a sequence to use
Seq = Seq2
StepCount = StepCount2

def to90grados():
    for angle in range(0,100,100):
        duty_cycle = 2.5 + (angle/18.0)
        p.ChangeDutyCycle(duty_cycle)
        time.sleep(1)
        
def to0grados():
    for angle in range(110,-1,-110):
        duty_cycle = 2.5 +(angle/18.0)
        p.ChangeDutyCycle(duty_cycle)
        time.sleep(1)
        
def steps(nb):
        StepCounter = 0
        if nb<0: sign=-1
        else: sign=1
        nb=sign*nb*2 #times 2 because half-step
        print("nbsteps {} and sign {}".format(nb,sign))
        for i in range(nb):
                for pin in range(4):
                        xpin = StepPins[pin]
                        if Seq[StepCounter][pin]!=0:
                                GPIO.output(xpin, True)
                        else:
                                GPIO.output(xpin, False)
                StepCounter += sign
        # If we reach the end of the sequence
        # start again
                if (StepCounter==StepCount):
                        StepCounter = 0
                if (StepCounter<0):
                        StepCounter = StepCount-1
                # Wait before moving on
                time.sleep(WaitTime)
# Start main loop
nbStepsPerRev=2048
siguiente=45
compuerta=1 #Compuerta al que quiero que vaya y vuelva, son 8 compuertas en totales 7 posibles.

def grados_a_pasos(grados):
    pasos = (grados/360)*nbStepsPerRev
    return int(pasos)

def retorno(grados):
    if (grados>180):
        grados = 360-grados
        steps(grados_a_pasos(grados))
    else:
        steps(-grados_a_pasos(grados))
        
def posicionExpulsion(grados):
    if(grados>180):
        grados = 360-grados
        steps(-grados_a_pasos(grados))
    else:
        steps(grados_a_pasos(grados))
        
def to90grados():
    for angle9 in range(0, 105, 5):
        duty_cycle9 = 2.5 + (angle9 / 18.0)
        p.ChangeDutyCycle(duty_cycle9)
        
        #time.sleep(0.5)
    print("Expulsar")
    
if __name__ == '__main__' :
    hasRun=False
    #GPIO.output(succionFan, GPIO.HIGH)
    #to90grados()
    #GPIO.output(empujeFan, GPIO.LOW)
    #time.sleep(5)
    #while not hasRun:
            #steps(grados_a_pasos(siguiente*compuerta))# parcourt un tour dans le sens horaire
            
    #posicionExpulsion(siguiente*2)
    #GPIO.output(16, GPIO.LOW)  # Se activa el succionador
    #to90grados()
    #GPIO.output(16, GPIO.HIGH) # Se desactiva el succionador
    #GPIO.output(succionFan, GPIO.LOW)
    #GPIO.output(empujeFan, GPIO.HIGH)
    #to0grados()
    #print("succion")
    #time.sleep(2)
    #steps(-grados_a_pasos(siguiente*compuerta))# parcourt un tour dans le sens anti-horaire
    retorno(siguiente*1)
    #GPIO.output(empujeFan, GPIO.LOW)
    #GPIO.output(succionFan, GPIO.HIGH)
    #to90grados()
    #print("EMPUJE")
    #time.sleep(5)
            #hasRun=True
    #print("Stop motor")
    #GPIO.output(succionFan, GPIO.LOW)
    #for pin in StepPins:
            #GPIO.output(pin, False)