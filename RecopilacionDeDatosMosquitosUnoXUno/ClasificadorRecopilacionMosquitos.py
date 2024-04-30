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
from scipy.fftpack import fft, ifft
from scipy.io.wavfile import write
from datetime import datetime
import os
import cv2
from collections import Counter
import wave
import shutil


GPIO.cleanup()
# Inicializar el gráfico
# plt.ion()  # Habilitar modo interactivo
# fig, ax = plt.subplots()
# line, = ax.plot([], [])
# ax.set_title('FFT en tiempo real')
# ax.set_xlabel('Frecuencia (Hz)')
# ax.set_ylabel('Amplitud')
# frecuencias = np.fft.fftfreq(512, 1 / 44100)  # Ajustar según el tamaño del periodo
# ax.set_xlim(0,  6000)  # Ajustar según la frecuencia de muestreo
# ax.set_ylim(-1800000, 1800000)
longitud_senal = 1024  # Tamanho del bufer de lectura
frecuencia_muestreo = 44100  # Establecer la frecuencia de muestreo a 42.667 kHz

tiempoDelay = 1.5  # El tiempo necesario para no detectar un falso negativo
puertoCamara = 0
puertoMicrofono = 2
carpetaDatos = "datos"
# Use BCM GPIO references
# Instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO signals to use Pins 18,22,24,26 GPIO24,GPIO25,GPIO8,GPIO7
StepPins = [17, 18, 27, 22]
# Set all pins as output

# Definir fan de succion y de empuje
servoPIN = 13
pinSuccionador = 16
pin_sensor_selector = 26
# succionFan = 6
# empujeFan = 5
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(succionFan, GPIO.OUT)
# GPIO.setup(empujeFan, GPIO.OUT)
GPIO.setup(servoPIN, GPIO.OUT)
servoCompuertaPIN = 6
GPIO.setup(servoCompuertaPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50)  # SERVO DEL SELECTOR FLUJO
p.start(2.5)
# --------------------------------------------------
c = GPIO.PWM(servoCompuertaPIN, 50)  # servo del compuerta mosquito
c.start(2.5)
# --------------------------------------------------
# Define el número del pin GPIO que deseas usar
pin_sensor = 5
# Configura el pin como entrada sensor
GPIO.setup(pin_sensor, GPIO.IN)
GPIO.setup(pin_sensor_selector, GPIO.IN)
# Configura el pin para salida digital on/off para el succionador controlador por el relay
GPIO.setup(pinSuccionador, GPIO.OUT)
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
    for angle9 in range(0, 130, 5):
        duty_cycle9 = 2.5 + (angle9 / 18.0)
        p.ChangeDutyCycle(duty_cycle9)
    print("Valvula Expulsar")


def to0grados():
    for angle0 in range(110, -1, -5):
        duty_cycle0 = 2.5 + (angle0 / 18.0)
        p.ChangeDutyCycle(duty_cycle0)
    print("Valvula Succionar")


def compuertaAbierta():
    for angleY in range(0, 61, 5):
        duty_cycley = 2.5 + (angleY / 18.0)
        c.ChangeDutyCycle(duty_cycley)
    print("Abierta")


def compuertaCerrado():
    for angleA in range(60, -1, -5):
        duty_cycleA = 2.5 + (angleA / 18.0)
        c.ChangeDutyCycle(duty_cycleA)  # Cuando esta abierto
    print("Cerrado")


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
grados = 45


def grados_a_pasos(grados):
    pasos = (grados / 360) * nbStepsPerRev
    return int(pasos)


def retorno(grados):
    if (grados > 180):
        grados = 360 - grados
        steps(grados_a_pasos(grados))
    else:
        steps(-grados_a_pasos(grados))


def gradosPosicion(grados):
    if (grados > 180 and grados != 0):
        grados = 360 - grados
        steps(-grados_a_pasos(grados))
    elif (grados != 0):
        steps(grados_a_pasos(grados))
    print('Seleccionador en posicion')


def deteccionMosquito():
    estado = 1
    while True:
        # Lee el valor del pin GPIO
        value = GPIO.input(pin_sensor)
        if value == GPIO.LOW:
            if estado == 1:
                tiempo_inicio = time.time()  # Inicia el temporizador
                estado = 2
            tiempo_baja = abs(time.time() - tiempo_inicio)
            if tiempo_baja >= tiempoDelay:
                print('Se procede a la deteccion del mosquito')
                break
        else:
            estado = 1


from collections import Counter

from collections import Counter


def clasificar_frecuencia(high_magnitude_freq):
    try:
        high_magnitude_freq = [freq for freq in high_magnitude_freq if freq is not None]
        print("high_magnitude_freq:", high_magnitude_freq)

        # Verificar si la lista de frecuencias no está vacía
        if not high_magnitude_freq:
            print("Lista vacía.")
            return None

        # Frecuencias correspondientes a cada especie
        rangos = {
            "aedes_albopictus_macho": (450, 550),
            "aedes_albopictus_hembra": (730, 880),
            "culex_pipiens_macho": (360, 480),
            "culex_pipiens": (550, 730)
        }

        # Contador para contar la frecuencia de cada especie
        conteo_especies = Counter()

        # Iterar sobre las frecuencias y clasificarlas
        for freq in high_magnitude_freq:
            for especie, rango in rangos.items():
                if rango[0] <= freq <= rango[1]:
                    conteo_especies[especie] += 1

        # Obtener la especie con mayor frecuencia
        especie_mas_comun = conteo_especies.most_common(1)
        if especie_mas_comun:
            return especie_mas_comun[0][0]  # Devuelve la especie más común
        else:
            return None  # Devuelve None si no se detecta ninguna especie dentro de los rangos
    except Exception as e:
        print("Error:", e)
        return None  # Devuelve None si ocurre algún error durante el proceso de clasificación


def capturar_foto(carpeta_fecha_hora,nombre):
    cap = cv2.VideoCapture(puertoCamara)  # Es el puerto donde se encuentra conectada la cámara web por USB
    # Verificar si la cámara está disponible
    if not cap.isOpened():
        print("Error: No se puede acceder a la cámara. ¿Está conectada correctamente?")
        return

    # Ajustar la resolución de la cámara
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 700)

    # Ruta completa de la imagen dentro de la carpeta de la fecha actual
    nombre_archivo = nombre+'.jpg'
    ruta_imagen = os.path.join(carpetaDatos, carpeta_fecha_hora, nombre_archivo)

    tiempo_inicial = time.time()
    brillo_maximo = 0
    while time.time() - tiempo_inicial < 1.5:
        ret, frame = cap.read()
        if ret:
            # Aplicar un filtro de enfoque a la imagen capturada
            frame_enfocado = cv2.GaussianBlur(frame, (5, 5), 0)
            # Calcular el brillo de la imagen
            brillo = cv2.mean(frame_enfocado)[0]
            # Guardar la imagen con el brillo máximo
            if brillo > brillo_maximo:
                brillo_maximo = brillo
                frame_maximo = frame_enfocado.copy()

    cv2.imwrite(ruta_imagen, frame_maximo)
    cap.release()
class SoundDetector:
    def __init__(self):
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 512
        self.RECORD_SECONDS = 5
        self.LOCALDATE = None

    def obtener_fecha_guardada(self):
        if(self.LOCALDATE!=None):
            return self.LOCALDATE
        else:
            return None
    def record_and_analyze(self, filename, save_plot_filename=None, input_device_index=None, repeat=False):
        while True:
            if input_device_index is None:
                input_device_index = self.get_default_input_device_index()

            stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, cardindex=input_device_index)
            stream.setchannels(self.CHANNELS)
            stream.setrate(self.RATE)
            stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            stream.setperiodsize(self.CHUNK)

            print("Grabando...")

            frames = []
            data = []

            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                length, audio_data = stream.read()
                frames.append(audio_data)
                data.extend(np.frombuffer(audio_data, dtype=np.int16))

            print("Fin de la grabación.")
            stream.close()

            # Guardar los datos de audio en un archivo WAV
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(2)  # 2 bytes para formato PCM_FORMAT_S16_LE
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            # Procesamiento de los datos grabados
            data = np.array(data)

            fft_data = np.fft.fft(data)
            fft_freq = np.fft.fftfreq(len(data), 1 / self.RATE)
            magnitude_spectrum = np.abs(fft_data)

            # Identificar frecuencias que superan la magnitud de 0.2 dentro del rango de frecuencia especificado
            high_magnitude_indices = np.where((magnitude_spectrum > 0.5) & (fft_freq >= 200) & (fft_freq <= 1000))[0]
            high_magnitude_freq = fft_freq[high_magnitude_indices]

            # Visualización del espectro de magnitud
            plt.figure(figsize=(8, 4))
            plt.plot(fft_freq[:len(fft_freq) // 2], magnitude_spectrum[:len(fft_freq) // 2])
            plt.xlabel('Frecuencia (Hz)')
            plt.ylabel('Magnitud')
            plt.title('Espectro de Magnitud')
            plt.grid(True)

            # Resaltar las frecuencias que superan la magnitud de 0.2 dentro del rango de frecuencia especificado
            plt.plot(high_magnitude_freq, magnitude_spectrum[high_magnitude_indices], 'ro', markersize=5)

            plt.xlim(0, self.RATE / 15)  # Limitar la visualización a frecuencias positivas
            plt.ylim(0, None)  # Limitar la visualización a magnitudes positivas

            # Guardar la imagen si se proporciona un nombre de archivo
            # Guardar la imagen si se proporciona un nombre de archivo
            print(save_plot_filename)
            if save_plot_filename:
                datos_folder = "datos"
                if not os.path.exists(datos_folder):
                    os.makedirs(datos_folder)  # Crea la carpeta "datos" si no existe

                # Crear la subcarpeta con la fecha actual si no existe
                subcarpeta_fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                carpeta_completa = os.path.join(datos_folder, subcarpeta_fecha)
                if not os.path.exists(carpeta_completa):
                    os.makedirs(carpeta_completa)  # Crea la subcarpeta con la fecha actual si no existe

                # Guardar la imagen dentro de la carpeta con la fecha actual
                filename_plot = os.path.join(carpeta_completa, save_plot_filename)
                plt.savefig(filename_plot)

                # Guardar el archivo de audio dentro de la carpeta con la fecha y hora actual
                filename_audio = os.path.join(carpeta_completa, filename)
                os.makedirs(carpeta_completa, exist_ok=True)  # Crear la carpeta si no existe
                os.rename(filename, filename_audio)
                print("Se guardan los audios y imagen de la frecuencia")
                self.LOCALDATE = subcarpeta_fecha
            # Imprimir las frecuencias que superan la magnitud de 0.2 dentro del rango de frecuencia especificado
            print("Frecuencias que superan la magnitud de 0.2 dentro del rango de 100 Hz a 1000 Hz:", high_magnitude_freq)
            return high_magnitude_freq
            if not repeat:
                break

    def get_default_input_device_index(self):
        # Devuelve el primer índice de dispositivo
        return 2


def mapear_clasificacion(clasificacion):
    if clasificacion == "aedes_albopictus_macho":
        return 1
    elif clasificacion == "aedes_albopictus_hembra":
        return 2
    elif clasificacion == "culex_pipiens_macho":
        return 3
    elif clasificacion == "culex_pipiens":
        return 4
    else:
        return 0

def imprimir_clasificacion(clasificacion):
    if clasificacion:
        print("La clasificación más probable es:", clasificacion)
        return clasificacion
    else:
        print("No se pudo determinar la clasificación.")
        return None


def apagarServo():
    p.ChangeDutyCycle(0)        
    print("apagar")
def encenderServo():
    p.start(11)


if __name__ == '__main__':
    hasRun = False
    to0grados()
    time.sleep(2)
    GPIO.output(pinSuccionador, GPIO.LOW)
    try:
        while not hasRun:
            print('-------Inicio Ciclo')
            encenderServo()
            time.sleep(1)
            to0grados()
            time.sleep(1)
            apagarServo()
            # compuertaAbierta()  # Se mantiene abierto siempre que no haya mosquitos dentro del seleccionador
            GPIO.output(pinSuccionador, GPIO.LOW)
            deteccionMosquito()  # No pasa de esta linea hasta que entre un mosquito
            # Se a detectado un mosquito se procede a cerrar las compuertas.
            # compuertaCerrado()
            # Se espera detectar dentro de la capsula
            # deteccionMosquitoDentroDeLaCapsula()#Una vez detectado continua con el flujo
            gradosPosicion(grados * 1)  # Se posiciona en la posicion en donde se encuentra el microfono para la deteccion
            print("Para el succionador")
            GPIO.output(pinSuccionador, GPIO.HIGH)
            time.sleep(4)
            print('Se procede a la clasificacion del mosquito')
            # Configurar el microfono fuera de la funcion
            # Ejecutar el detector de frecuencia con la configuracion del microfono
            compuertaPosicion = 0
            estadoDeteccion = False
            while not estadoDeteccion:
                # Uso de la clase SoundDetector
                high_magnitude_freq = None
                detector = SoundDetector()
                high_magnitude_freq = detector.record_and_analyze("grabacion.wav", save_plot_filename="spectrogram.png", input_device_index=2, repeat=False)  # Cambia el valor de input_device_index según tu dispositivo
                print(high_magnitude_freq)
                clasificacion = clasificar_frecuencia(high_magnitude_freq)
                print(clasificacion)
                #nombreMosquito=imprimir_clasificacion(clasificacion)
                #compuertaPosicion = mapear_clasificacion(clasificacion)
                compuertaPosicion = 1
                if(compuertaPosicion is None):
                    carpeta_fecha_actual = os.path.join("datos", detector.obtener_fecha_guardada())
                    if os.path.exists(carpeta_fecha_actual):
                        shutil.rmtree(carpeta_fecha_actual)
                        print(f"Carpeta {carpeta_fecha_actual} eliminada correctamente")
                if compuertaPosicion != 0:
                    GPIO.output(pinSuccionador, GPIO.LOW)  # Se activa el succionador
                    time.sleep(3)
                    gradosPosicion(grados * 1)  # Se mueve a la posicion de la camara verificar esto/////////
                    GPIO.output(pinSuccionador, GPIO.HIGH)  # Paramos el succionador para sacarle una foto
                    time.sleep(2)

                    if(detector.obtener_fecha_guardada() is not None):
                        fechaGuardada = detector.obtener_fecha_guardada()
                        capturar_foto(fechaGuardada,"MosquitoSinClasificar")
                        print('Se guarda la imagen del mosquito')

                    # ---------Se guarda el audio y la imagen------
                    GPIO.output(pinSuccionador, GPIO.LOW)  # Volvemos a activar el succionador para mover
                    time.sleep(1)
                    print(f'Se detecto el tipo de mosquito para la compuerta:{compuertaPosicion}')
                    gradosPosicion(grados * compuertaPosicion)
                    encenderServo()
                    to90grados()
                    time.sleep(10)
                    retorno(grados * (compuertaPosicion + 2))
                    GPIO.output(pinSuccionador, GPIO.HIGH)  # Apagamos el succionar mientras
                    #retorno(grados * (compuertaPosicion + 2))
                    compuertaPosicion = 0
                    estadoDeteccion = True

    except KeyboardInterrupt:
        c.stop()
        GPIO.cleanup()
        print("Cleanup gpio")
        # hasRun=True
        print("Stop motor")
        # GPIO.output(succionFan, GPIO.LOW)
        for pin in StepPins:
            GPIO.output(pin, False)
