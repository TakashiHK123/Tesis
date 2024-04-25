

import RPi.GPIO as GPIO
import time

# Configura el modo de la GPIO
GPIO.setmode(GPIO.BCM)

# Define el número del pin GPIO que deseas usar
pin_sensor = 5

# Configura el pin como entrada
GPIO.setup(pin_sensor, GPIO.IN)
tiempoDelay=1.5
def deteccionMosquito():
    estado=1
    while True:
        # Lee el valor del pin GPIO
        value = GPIO.input(pin_sensor)
        if value == GPIO.LOW:
            if estado==1:
                tiempo_inicio = time.time() #Inicia el temporizador
                estado=2
            tiempo_baja = abs(time.time() - tiempo_inicio)
            if tiempo_baja >= tiempoDelay:
                print('Se procede a la deteccion del mosquito')
                break
        else:
            estado = 1
print('Se inicia la deteccion')
deteccionMosquito()
print('Se a detectado y a pasado')