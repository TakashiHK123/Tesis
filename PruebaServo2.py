import RPi.GPIO as GPIO
import time

servoPIN = 6  # Ajusta esto según el pin GPIO que estás utilizando
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

pwm = GPIO.PWM(servoPIN, 50)  # Frecuencia de 50 Hz (generalmente es estándar)
pwm.start(7.5)  # Pulso inicial (puedes ajustarlo según tus necesidades)

try:
    while True:
        pwm.ChangeDutyCycle(5.5)  # 90 grados
        time.sleep(1)
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()