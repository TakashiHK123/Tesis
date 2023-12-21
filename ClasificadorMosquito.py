#!/usr/bin/env python
# -*- coding: utf-8 -*-
# libraries
import RPi.GPIO as GPIO
import numpy as np
import scipy.io.wavfile as wav
import alsaaudio
import time
import pyudev
import matplotlib.pyplot as plt

# Inicializar el gráfico
plt.ion()  # Habilitar modo interactivo
fig, ax = plt.subplots()
line, = ax.plot([], [])
ax.set_title('FFT en tiempo real')
ax.set_xlabel('Frecuencia (Hz)')
ax.set_ylabel('Amplitud')
#frecuencias = np.fft.fftfreq(512, 1 / 44100)  # Ajustar según el tamaño del periodo
ax.set_xlim(0,  6000)  # Ajustar según la frecuencia de muestreo
ax.set_ylim(-1800000, 1800000)
longitud_senal = 1024 #Tamanho del bufer de lectura
frecuencia_muestreo = 44100 # Establecer la frecuencia de muestreo a 42.667 kHz

# Use BCM GPIO references
# Instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
# Define GPIO signals to use Pins 18,22,24,26 GPIO24,GPIO25,GPIO8,GPIO7
StepPins = [17, 18, 27, 22]
# Set all pins as output

# Definir fan de succion y de empuje
servoPIN = 13
# succionFan = 6
# empujeFan = 5
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(succionFan, GPIO.OUT)
# GPIO.setup(empujeFan, GPIO.OUT)
GPIO.setup(servoPIN, GPIO.OUT)
servoCompuertaPIN = 6
GPIO.setup(servoCompuertaPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50)  #SERVO DEL SELECTOR FLUJO
p.start(2.5)
# --------------------------------------------------
c = GPIO.PWM(servoCompuertaPIN, 50) #servo del compuerta mosquito
c.start(2.5)
# --------------------------------------------------
# Define el número del pin GPIO que deseas usar
pin_sensor = 5
# Configura el pin como entrada
GPIO.setup(pin_sensor, GPIO.IN)

for pin in StepPins:
    print("Setup pins")
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)
# Define some settings
WaitTime = 0.005
# Define simple sequence
StepCount1 = 4
Seq1 = []
Seq1 = [i for i in range(0, StepCount1)]
Seq1[0] = [1, 0, 0, 0]
Seq1[1] = [0, 1, 0, 0]
Seq1[2] = [0, 0, 1, 0]
Seq1[3] = [0, 0, 0, 1]
# Define advanced half-step sequence
StepCount2 = 8
Seq2 = []
Seq2 = [i for i in range(0, StepCount2)]
Seq2[0] = [1, 0, 0, 0]
Seq2[1] = [1, 1, 0, 0]
Seq2[2] = [0, 1, 0, 0]
Seq2[3] = [0, 1, 1, 0]
Seq2[4] = [0, 0, 1, 0]
Seq2[5] = [0, 0, 1, 1]
Seq2[6] = [0, 0, 0, 1]
Seq2[7] = [1, 0, 0, 1]
# Choose a sequence to use
Seq = Seq2
StepCount = StepCount2


def to90grados():
    for angle in range(0, 100, 100):
        duty_cycle = 2.5 + (angle / 18.0)
        p.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)


def to0grados():
    for angle in range(110, -1, -110):
        duty_cycle = 2.5 + (angle / 18.0)
        p.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)

def compuertaAbierta():
    for angle in range(60,-1,-60):
        duty_cycle = 2.5 +(angle/18.0)
        c.ChangeDutyCycle(duty_cycle)#Cuando esta abierto
        time.sleep(0.5)

def compuertaCerrada():
    for angleY in range(0,60,60):
        duty_cycle = 2.5 + (angleY/18.0)
        c.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)

def steps(nb):
    StepCounter = 0
    if nb < 0:
        sign = -1
    else:
        sign = 1
    nb = sign * nb * 2  # times 2 because half-step
    print("nbsteps {} and sign {}".format(nb, sign))
    for i in range(nb):
        for pin in range(4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin] != 0:
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
        StepCounter += sign
        # If we reach the end of the sequence
        # start again
        if (StepCounter == StepCount):
            StepCounter = 0
        if (StepCounter < 0):
            StepCounter = StepCount - 1
        # Wait before moving on
        time.sleep(WaitTime)


# Start main loop
nbStepsPerRev = 2048
siguiente = 45
compuerta = 1  # Compuerta al que quiero que vaya y vuelva, son 8 compuertas en totales 7 posibles.


def grados_a_pasos(grados):
    pasos = (grados / 360) * nbStepsPerRev
    return int(pasos)


def retorno(grados):
    if (grados > 180):
        grados = 360 - grados
        steps(grados_a_pasos(grados))
    else:
        steps(-grados_a_pasos(grados))


def posicionExpulsion(grados):
    if (grados > 180):
        grados = 360 - grados
        steps(-grados_a_pasos(grados))
    else:
        steps(grados_a_pasos(grados))


def deteccionMosquito():
    # Lee el valor del pin GPIO
    value = GPIO.input(pin_sensor)
    estado = 0 #estados 0 aun no se detecto el mosquito, 1 se a detectado
    detected = False
    while not detected:

        if value == GPIO.HIGH:
            print('Mosquito detectado: Se espera a que pase todo para cerrar la compuerta')
            estado = 1
            print(value)
            return detected
            # Realiza acciones específicas para objetos blancos
        else:
            print('No hay mosquitos')
            if estado == 1:
                print('El mosquito a ingresado, proceder a cerrar la compuerta')
                estado = 0
                detected = True
                return detected
            print(value)
            return detected
            # Realiza acciones específicas para objetos negros

        # Espera un tiempo antes de la siguiente lectura
        time.sleep(0.01)


def es_dispositivo_usb(dispositivo):
    # Verificar si el directorio del dispositivo contiene "usb"
    return "usb" in dispositivo.device_path


def obtener_dispositivos_usb():
    context = pyudev.Context()
    dispositivos_usb = []

    for dispositivo in context.list_devices(subsystem='sound'):
        # print("Atributos disponibles para el dispositivo:")
        for atributo in dir(dispositivo.attributes):
            if not atributo.startswith('_'):
                valor = getattr(dispositivo.attributes, atributo)
                # print(f"{atributo}: {valor}")

        devtype = dispositivo.attributes.get('DEVTYPE')
        id_bus = dispositivo.attributes.get('ID_BUS')

        # print(f"devtype: {devtype}")
        # print(f"id_bus: {id_bus}")

        # Comprobamos si el dispositivo está en el bus USB
        if es_dispositivo_usb(dispositivo):
            dispositivos_usb.append(dispositivo.device_node)
            print("Este es un dispositivo USB de audio.")
        else:
            print("Este no es un dispositivo USB de audio.")

        print("\n---\n")

    return dispositivos_usb


def configurar_mic():
    dispositivos_usb = obtener_dispositivos_usb()
    if not dispositivos_usb:
        # print("No se encontraron dispositivos USB.")
        return None
    # print("Dispositivos USB encontrados:")
    # for i, dispositivo in enumerate(dispositivos_usb, 1):
    # print(f'{i}.{dispositivo}')

    seleccion = int(2)

    if 1 <= seleccion <= len(dispositivos_usb):

        # Configurar el micrófono seleccionado con 1 canal (mono)
        mic_configurado = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL,
                                        cardindex=2)  # Reemplaza 2 con tu cardindex
        mic_configurado.setchannels(1)  # Establecer el número de canales a 1 (mono)
        mic_configurado.setrate(frecuencia_muestreo)  # Establecer la frecuencia de muestreo a 44.1 kHz
        mic_configurado.setformat(alsaaudio.PCM_FORMAT_S16_LE)  # Establecer el formato de audio a 16 bits little-endian

        # Intenta con un tamaño de periodo más pequeño
        mic_configurado.setperiodsize(longitud_senal)  # Establecer el tamaño del periodo

        # Capturar datos
        return mic_configurado
    else:
        print("Seleccion no valida")
        return None
def detectar_frecuencia_usb(capturador):
    # Aplicar la Transformada Rapida de Fourier (FFT)

    umbral_db = -50
    plt.show(block=False)
    frecuencias = np.fft.fftfreq(longitud_senal, 1 / frecuencia_muestreo)
    amplitudes_iniciales = np.zeros(longitud_senal)
    line, = ax.plot(frecuencias, amplitudes_iniciales)
    detected = True
    try:
        while detected:

            # Leer datos del microfono USB
            longitud_buffer = len(capturador.read()[1])
            longitud_buffer = longitud_buffer - (longitud_buffer % 2)

            # Procesar los datos capturados
            datos = np.frombuffer(capturador.read()[1][:longitud_buffer], dtype=np.int16)
            # Realizar la FFT
            # Calcular nivel de decibelios RMS
            if datos is not None:
                rms_level_db = 20 * np.log10(np.sqrt(np.mean(datos ** 2)))
                # Calcular las frecuencias correspondientes
                fft_resultado = np.fft.fft(datos)

                # Calcular las frecuencias correspondientes
                frecuencias = np.fft.fftfreq(longitud_senal, 1 / frecuencia_muestreo)

                # Encontrar el indice de la frecuencia dominante
                indice_frecuencia_dominante = np.argmax(np.abs(fft_resultado))

                # Obtener la frecuencia dominante en Hz
                # Actualizar la línea en el gráfico
                line.set_xdata(np.abs(frecuencias))
                line.set_ydata(fft_resultado)
                # print(np.abs(fft_resultado))
                plt.draw()
                # Actualizar el gráfico
                plt.pause(0.001)  # Añadi un pequeño retraso para permitir la actualización de la interfaz gráfica
                frecuencia_dominante = frecuencias[indice_frecuencia_dominante]
                if frecuencia_dominante != 0 and frecuencia_dominante >= 300 and rms_level_db > umbral_db:
                    print(f'Decibelios:{rms_level_db}')
                    print(f'Frecuencia: {frecuencia_dominante} Hz')
                    time.sleep(0.01)
                    detected = False
                    return frecuencia_dominante
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    hasRun = False
    # GPIO.output(succionFan, GPIO.HIGH)
    to90grados()
    # GPIO.output(empujeFan, GPIO.LOW)
    time.sleep(5)
    mic_configurado = configurar_mic()
    #Se configura las etapa
    #etapa = 0 no se detecta aun mosquito
    #etapa = 1 se detecto el mosquito y a pasado al seleccionador para cerrar la compuerta
    #etapa = 2 el mosquito paso todo para cerrar la compuerta y proceder a la clasificacion
    while not hasRun:
        to0grados()
        compuertaAbierta()  # Se mantiene abierto siempre que no haya mosquitos dentro del seleccionador
        detectado = deteccionMosquito()
        if detectado==True:
            compuertaCerrada()
            print("Para el succionador")
            time.sleep(5)
            print('Se procede a la clasificacion del mosquito')
            # Configurar el microfono fuera de la funcion
            # Ejecutar el detector de frecuencia con la configuracion del microfono
            frecuencia = detectar_frecuencia_usb(mic_configurado)
            compuertaPosicion = 0
            if frecuencia >= 500 and frecuencia <=630:
                print('se a detectado un mosquito entre los rango 500 y 630')
                # steps(grados_a_pasos(siguiente*compuerta))# parcourt un tour dans le sens horaire
                compuertaPosicion=1 #seria la compuerta correspondiente a cierto mosquito
            if frecuencia >= 630 and frecuencia <=800:
                compuertaPosicion = 2

            if compuertaPosicion != 0:
                posicionExpulsion(siguiente * compuertaPosicion)
                to90grados()
                print("se enciende succionador para el empuje")
                time.sleep(5)
                retorno(siguiente * compuertaPosicion)
                compuertaPosicion = 0

        # hasRun=True
    print("Stop motor")
    # GPIO.output(succionFan, GPIO.LOW)
    for pin in StepPins:
        GPIO.output(pin, False)