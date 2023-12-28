import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Asume que el servo está conectado al pin GPIO18
SERVO_PIN = 6

GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50) # 50Hz frequency
pwm.start(0) # Duty cycle de 0 para que el servo esté parado

# Cambia el ángulo del servo en un rango de 0 a 180
def set_servo_angle(angle):
    duty = angle / 18.0 + 2.0
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        for angle in range(0, 61, 10): # Vibra entre 0 y 180 en pasos de 10
            set_servo_angle(angle)
            time.sleep(0.5)

except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()