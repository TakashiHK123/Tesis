import wiringpi
from wiringpi import GPIO
wiringpi.wiringPiSetup()

DEVICE_AS5600 = 0x36
fd = wiringpi.wiringPiI2CSetupInterface("/dev/i2c-2",DEVICE_AS5600)
    
def ReadRawAngle(): # Read angle (0-360 represented as 0-4096)
    read_bytes = (wiringpi.wiringPiI2CReadReg8(fd, 0x0C) & 31)<<8#0000 1111 1111 1111
    read_bytes+= wiringpi.wiringPiI2CReadReg8(fd, 0x0D)
    return ( read_bytes* 360.0) / 4096.0   

"""
-1: 245.3
 0: 289.6
 1: 336.5
 2: 19.9
 3: 65.9
 4: 110.5
 5: 155.1
 6: 200.3
 zona prohibida: 220

"""

posicionesAng={-1: 245.3, 0: 289.6, 1: 336.5, 2: 19.9+360, 3: 65.96+360, 4: 110.5+360, 5: 155.1+360, 6: 200.3+360, "prohibido":220}

def Angulo():
    ang=ReadRawAngle()
    if ang<posicionesAng["prohibido"]:
        return ang+360
    return ang


#stepper
microsteps=16
StepsPerRev=200*microsteps
global posActual
posActual=None
wiringpi.wiringPiSetup()
ENABLE=24
STEP=26
DIR=27
ENDSTOP=13

wiringpi.pinMode(ENDSTOP, GPIO.INPUT)
wiringpi.pinMode(ENABLE, GPIO.OUTPUT)
wiringpi.pinMode(STEP, GPIO.OUTPUT)
wiringpi.pinMode(DIR, GPIO.OUTPUT)

def setVel(vel):#grados/segundo
    global Tus
    Tus=int(1/(vel/360*(StepsPerRev))*500000)

setVel(60)

def step(n=1,direction=True):
    wiringpi.digitalWrite(DIR, direction)
    for j in range(n):
        wiringpi.digitalWrite(STEP, True)
        wiringpi.delayMicroseconds(Tus)
        wiringpi.digitalWrite(STEP, False)
        wiringpi.delayMicroseconds(Tus)
     


def goToPos(pos=0,encoder=1): 
    global posActual
    if (pos==posActual and not encoder) or pos>6 or pos <-1:
        return
    wiringpi.digitalWrite(ENABLE, False)
    wiringpi.delay(200)
    if encoder:
        obj=posicionesAng[pos]
        ang=Angulo()
        while(abs(ang-obj)>0.5):
            direction=ang>obj
            step(4,direction)
            ang=Angulo()
            
    else:
        if posActual==None:
            direction=True
            pos=0
        else:
            direction= posActual>pos
            dif=abs(posActual-pos)
        if pos==0:
            wiringpi.digitalWrite(DIR, direction)
            if not wiringpi.digitalRead(ENDSTOP):
                step(50,0)
            for i in range(StepsPerRev):
                if not wiringpi.digitalRead(ENDSTOP): 
                    if direction:
                        step(16)
                    else:
                        step(34,0)
                    break
                step(1,direction)
        else:
            step(int(dif*400),direction)

    posActual=pos
    wiringpi.delay(200)
    wiringpi.digitalWrite(ENABLE, True)

try:
    goToPos()
    while True:
        x=int(input("Pos: "))
        if x>10:
            x=int(input("Vel: "))
            setVel(x)
        else:
            goToPos(x)

except:# Exception as e:
    #print(e)
    pass
    
wiringpi.delay(200)
wiringpi.digitalWrite(ENABLE, True)
wiringpi.pinMode(STEP, GPIO.INPUT)
wiringpi.pinMode(DIR, GPIO.INPUT)
wiringpi.pinMode(ENABLE, GPIO.INPUT)