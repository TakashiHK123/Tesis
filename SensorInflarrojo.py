import RPi.GPIO as GPIO
import time

# Configura el modo de la GPIO
GPIO.setmode(GPIO.BCM)

# Define el número del pin GPIO que deseas usar
pin_sensor = 5

# Configura el pin como entrada
GPIO.setup(pin_sensor, GPIO.IN)

def deteccionMosquito():
    estado = 0 #estados 0 aun no se detecto el mosquito, 1 se a detectado
    while True:
        # Lee el valor del pin GPIO
        value = GPIO.input(pin_sensor)
        #print(f'Value={value}')
        if value == GPIO.HIGH:
            #print('Mosquito detectado: Se espera a que pase todo para cerrar la compuerta')
            estado = 1
            print(f'Estado:{estado}')
            # Realiza acciones específicas para objetos blancos
        else:
            print(f'Estado:{estado}')
            if estado == 1:
                print('El mosquito a ingresado, proceder a cerrar la compuerta')
                estado = 0
                break
            #print(value)
            
            # Realiza acciones específicas para objetos negros

        # Espera un tiempo antes de la siguiente lectura
        time.sleep(0.01)

detected = deteccionMosquito()
#print(detected)
print('Se a detectado y a pasado')