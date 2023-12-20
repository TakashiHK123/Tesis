import RPi.GPIO as GPIO
import time

# Configura el modo de la GPIO
GPIO.setmode(GPIO.BCM)

# Define el número del pin GPIO que deseas usar
pin_sensor = 5

# Configura el pin como entrada
GPIO.setup(pin_sensor, GPIO.IN)

while True:
    # Lee el valor del pin GPIO
    value = GPIO.input(pin_sensor)
    
    if value == GPIO.HIGH:
        print('Objeto blanco detectado')
        print(value)
        # Realiza acciones específicas para objetos blancos
    else:
        print('Objeto negro detectado')
        print(value)
        # Realiza acciones específicas para objetos negros
    
    # Espera un tiempo antes de la siguiente lectura
    time.sleep(1)