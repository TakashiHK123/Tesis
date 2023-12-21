import RPi.GPIO as GPIO
import time

# Configura el modo de la GPIO
GPIO.setmode(GPIO.BCM)

# Define el número del pin GPIO que deseas usar
pin_sensor = 5

# Configura el pin como entrada
GPIO.setup(pin_sensor, GPIO.IN)

def deteccionMosquito():
    while True:
        # Lee el valor del pin GPIO
        value = GPIO.input(pin_sensor)
        estado = 0 #estados 0 aun no se detecto el mosquito, 1 se a detectado
        if value == GPIO.HIGH:
            print('Mosquito detectado: Se espera a que pase todo para cerrar la compuerta')
            estado = 1
            print(value)
            # Realiza acciones específicas para objetos blancos
        else:
            print('No hay mosquitos')
            if estado == 1:
                print('El mosquito a ingresado, proceder a cerrar la compuerta')
                estado = 0
                return True
            print(value)
            # Realiza acciones específicas para objetos negros

        # Espera un tiempo antes de la siguiente lectura
        time.sleep(0.01)
