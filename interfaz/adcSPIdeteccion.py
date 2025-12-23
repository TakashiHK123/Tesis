import wiringpi
from wiringpi import GPIO
import numpy as np
import matplotlib.pyplot as plt


import os 

SCLK = 25
MISO = 22
MOSI = 23
DRDY = 20
CS2 = 19

wiringpi.wiringPiSetup()

wiringpi.pinMode(SCLK, GPIO.OUTPUT)
wiringpi.pinMode(MOSI, GPIO.OUTPUT)
wiringpi.pinMode(CS2, GPIO.OUTPUT)

wiringpi.pinMode(MISO, GPIO.INPUT)
wiringpi.pinMode(DRDY, GPIO.INPUT)

#wiringpi.pinMode(27, GPIO.OUTPUT)
#wiringpi.digitalWrite(27, True)

def pulsePin(pin):
	#wiringpi.digitalWrite(pin, True)
	wiringpi.digitalWrite(pin, True)
	wiringpi.digitalWrite(pin, False)
	return
	
def enviar(bit):
	wiringpi.digitalWrite(MOSI, bit)
	pulsePin(SCLK)
	
def recivir():
	pulsePin(SCLK)	
	return wiringpi.digitalRead(MISO)	
	
def pruebaVel():
	rep=10000000
	comienzo=wiringpi.micros()
	for i in range(rep):
		recivir()
	tiempo=wiringpi.micros()-comienzo
	print(tiempo/1000000,"s")
	print(tiempo/rep,"us por lectura ",rep/tiempo," MHZ")

	rep=10000000
	comienzo=wiringpi.micros()
	for i in range(rep):
		enviar(0)
	tiempo=wiringpi.micros()-comienzo
	print(tiempo/1000000,"s")
	print(tiempo/rep,"us por escritura ",rep/tiempo," MHZ")
	"""
	84.605774 s
	8.4605774 us por lectura  0.11819524279749512  MHZ
	94.347855 s
	9.4347855 us por escritura  0.10599075092910168  MHZ
	3.5949814319610596
	"""
	return

#wiringpi.digitalWrite(CS2, True)
#pruebaVel()	

wiringpi.digitalWrite(CS2, False)

#seleccion de ADC
#0x01   76 o 01
#msg=0x510076 #7 positivo y 6 negativo
msg=0x510001 #default 0 positivo y 1 negativo
#msg=0x510002
#msg=0x510012
for i in range(24):
	enviar(msg & 0x800000)
	msg = msg << 1
wiringpi.delayMicroseconds(10)

#SPS
#msg=0x5300D0#11010000 = 7,500SPS
#msg=0x5300A1#10100001 = 1,000SPS
msg=0x5300B0 #2k sps
#msg=0x5300C0 #3.75k sps
#msg =0x530023 #00100011 = 10SPS
for i in range(24):
	enviar(msg & 0x800000)
	msg = msg << 1
wiringpi.delayMicroseconds(10)

#RDATAC
msg = 0x03
for i in range(8):
	enviar(msg & 0x80)
	msg = msg << 1
wiringpi.delayMicroseconds(10)


c=[[],[]]
entradasM=[]
salidasM=[]

def funcion2(val,x):
    m=np.mean(val)
    if (max(val)>m+0.001) and (min(val)<m-0.0003):
        i=np.argmax(val)
        j=np.argmin(val)
        #print("thmna")
        if j>i:#0<j-i<11:
            if (max(val)>np.mean(val[:i+1])+0.0005) and (min(val)<np.mean(val[j:])-0.00015):
                c[0].append(x+i)
                c[1].append(x+j)
                entradasM.append((i+j)//2+x)
                #print("aaaaaaaaaa")
                return 1
        else:
            if (max(val)>np.mean(val[i:])+0.0005) and (min(val)<np.mean(val[:j+1])-0.00015):
                c[0].append(x+i)
                c[1].append(x+j)
                salidasM.append((i+j)//2+x)
                #print("bbbbbbbbbbbbb")
    return 0


n=int(120000/2)
datos=np.zeros(n)#,dtype="int32")
k=0
print("comienzo")
while(not wiringpi.digitalRead(DRDY)):
    pass
tiempo=wiringpi.millis()

for i in range(n):
	out=0x000000
	#if i==0:
	while(wiringpi.digitalRead(DRDY)):
		pass
	for	j in range(24):#entre 1 y 24, dependiendo de cuantos bits se quieren leer
		aux = recivir() & 0x000001
		aux = aux <<(23-j)
		out += aux
        
	while(not wiringpi.digitalRead(DRDY)):
		pass
        
	signo=out & 0x800000
	out= out  & 0x7FFFFF
	if signo!=0:
		out = -(((~out) & 0x7FFFFF )+1)
	#print(out/8388608*5)
	datos[i]=out/8388608*5.0

	if i%5==0 and i>15:
		if k:
			k-=1
		else:
			k=funcion2(datos[i-14:i+1],i-14)*3



tiempo=(wiringpi.millis()-tiempo)/1000
print("tiempo: ",tiempo, "s Frecuencia: ",n/tiempo)



#SDATAC: Stop Read Data Continuous
msg = 0x0F
while(wiringpi.digitalRead(DRDY)):
	pass
for i in range(8):
	enviar(msg & 0x80)
	msg = msg << 1

wiringpi.digitalWrite(CS2, True)


plt.figure(1)
plt.plot(datos)
plt.scatter(entradasM,datos[entradasM],color="m",marker=">")
plt.scatter(salidasM,datos[salidasM],color="y",marker="<")
plt.scatter(c[0],datos[c[0]],color="r",marker="o")
plt.scatter(c[1],datos[c[1]],color="g",marker="o")
plt.title(" Entradas: "+str(len(entradasM))+"  Salidas: "+str(len(salidasM)))
#print(datos.max(),datos.min(),datos.mean())
print("Media: ",np.mean(datos),"v Max: ",np.max(datos),"v Min: ",np.min(datos),"v")



plt.show()


x=input("Guardar? y/n: ")
if x.lower()=="y":
    x="entradaMosquitos"
    archivos=os.listdir("mediciones/entrada/")
    archivo=x + ".csv"
    c=2
    while archivo in archivos:
        archivo=x+"_"+str(c) + ".csv"
        c+=1
    archivo="mediciones/entrada/" + archivo
    with open(archivo, "w") as f:
        for i in datos:
            f.write(str(i)+"\n")
