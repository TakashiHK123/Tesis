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
from scipy.fft import fft, ifft
from scipy.io.wavfile import write
import datetime
import os
import cv2


GPIO.cleanup()
# Inicializar el gráfico
#plt.ion()  # Habilitar modo interactivo
#fig, ax = plt.subplots()
#line, = ax.plot([], [])
#ax.set_title('FFT en tiempo real')
#ax.set_xlabel('Frecuencia (Hz)')
#ax.set_ylabel('Amplitud')
#frecuencias = np.fft.fftfreq(512, 1 / 44100)  # Ajustar según el tamaño del periodo
#ax.set_xlim(0,  6000)  # Ajustar según la frecuencia de muestreo
#ax.set_ylim(-1800000, 1800000)
longitud_senal = 1024 #Tamanho del bufer de lectura
frecuencia_muestreo = 44100 # Establecer la frecuencia de muestreo a 42.667 kHz


puertoCamara=0
puertoMicrofono=2
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
p = GPIO.PWM(servoPIN, 50)  #SERVO DEL SELECTOR FLUJO
p.start(2.5)
# --------------------------------------------------
c = GPIO.PWM(servoCompuertaPIN, 50) #servo del compuerta mosquito
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
    for angle9 in range(0, 105, 5):
        duty_cycle9 = 2.5 + (angle9 / 18.0)
        p.ChangeDutyCycle(duty_cycle9)
    print("Valvula Expulsar")


def to0grados():
    for angle0 in range(100, -1, -5):
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
    if (grados > 180 and grados!=0):
        grados = 360 - grados
        steps(-grados_a_pasos(grados))
    elif(grados!=0):
        steps(grados_a_pasos(grados))
    print('Seleccionador en posicion')

def deteccionMosquito():
    estado = 0  # estados 0 aun no se detecto el mosquito, 1 se a detectado

    while True:
        # Lee el valor del pin GPIO
        value = GPIO.input(pin_sensor)
        if value == GPIO.HIGH:
            estado = 1
        else:
            if estado == 1:
                print('Se procede a la deteccion del mosquito')
                break

def deteccionMosquitoDentroDeLaCapsula():
    estado = 0  # estados 0 aun no se detecto el mosquito, 1 se a detectado
    while True:
        # Lee el valor del pin GPIO
        value = GPIO.input(pin_sensor_selector)

        if value == GPIO.HIGH:
            estado = 1
        else:
            if estado == 1:
                print('Mosquito ingresado dentro de la capsula')
                estado = 0
                break
            # Realiza acciones específicas para objetos negros

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
        print("No se encontraron dispositivos USB.")
        return None
    # print("Dispositivos USB encontrados:")
    # for i, dispositivo in enumerate(dispositivos_usb, 1):
    # print(f'{i}.{dispositivo}')

    seleccion = int(2)

    if 1 <= seleccion <= len(dispositivos_usb):

        # Configurar el micrófono seleccionado con 1 canal (mono)
        mic_configurado = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, cardindex=puertoMicrofono)  # Reemplaza 2 con tu cardindex
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
    #plt.show(block=False)
    #frecuencias = np.fft.fftfreq(longitud_senal, 1 / frecuencia_muestreo)
    #amplitudes_iniciales = np.zeros(longitud_senal)
    #line, = ax.plot(frecuencias, amplitudes_iniciales)
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
            if np.any(datos)==False:
                print('El valor del microfono es zero')
            else:
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
                    #line.set_xdata(np.abs(frecuencias))
                    #line.set_ydata(fft_resultado)
                    # print(np.abs(fft_resultado))
                    #plt.draw()
                    # Actualizar el gráfico
                    #plt.pause(0.001)  # Añadi un pequeño retraso para permitir la actualización de la interfaz gráfica
                    frecuencia_dominante = frecuencias[indice_frecuencia_dominante]
                    if frecuencia_dominante != 0 and frecuencia_dominante >= 300 and rms_level_db > umbral_db and frecuencia_dominante <= 1000:
                        print(f'Decibelios:{rms_level_db}')
                        print(f'Frecuencia: {frecuencia_dominante} Hz')
                        time.sleep(0.01)
                        #signal_reconstruida = ifft(fft_resultado)
                        #fft_resultado_padded = np.pad(fft_resultado, (0, frecuencia_muestreo - len(fft_resultado)))
                        # Reconstruir la señal en el dominio del tiempo utilizando la IFFT
                        #signal_reconstruida = np.real(ifft(fft_resultado_padded))
                        signal_reconstruida = capturador.read()[1]
                        detected = False
                        return [frecuencia_dominante,signal_reconstruida]
    except KeyboardInterrupt:
        pass
def selectorCompuertaByRangoFrecuencia(frecuencia,minimo,maximo,compuerta,detectado):
    if frecuencia >= minimo and frecuencia <= maximo:
        print(f'Se a detectado un mosquito entre los rangos de frecuencia:{minimo} - {maximo} para compuerta:{compuerta}')
        # steps(grados_a_pasos(grados*compuerta))# parcourt un tour dans le sens horaire
        return compuerta
    return detectado

def capturar_foto(carpeta_mosquitos):
    cap = cv2.VideoCapture(puertoCamara) #es el puerto en donde se encuentra conectado la camara web por usb

    # Verificar si la cámara está disponible
    if not cap.isOpened():
        print("Error: No se puede acceder a la cámara. ¿Está conectada correctamente?")
        return
    # Crear la carpeta del mosquito si no existe
    if not os.path.exists(carpeta_mosquitos):
        os.makedirs(carpeta_mosquitos)
    #carpeta_mosquitos = os.path.join(nombre_archivo, nombre_carpeta_mosquitos)

    # Ruta completa de la imagen dentro de la carpeta 'imagenes'
    nombre_archivo='imagen.jpg'
    ruta_imagen = os.path.join(carpeta_mosquitos, nombre_archivo)

    ret, frame = cap.read()
    cv2.imwrite(ruta_imagen, frame)
    cap.release()


def guardar_datos(numero_mosquito, audio_data, frecuencia_muestreo):
    # Obtener la fecha y hora actual para el nombre de archivo
    formato_fecha_hora = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # Crear la ruta base
    ruta_carpeta = f'datos/mosquitos{numero_mosquito}_{formato_fecha_hora}'

    # Crear la carpeta del mosquito si no existe
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)
    # Guardar el archivo de audio
    nombre_audio = f'{ruta_carpeta}/audio.wav'
    write(nombre_audio, frecuencia_muestreo, audio_data)

    # Capturar una foto y guardarla
    ruta_carpeta = f'{ruta_carpeta}'
    capturar_foto(ruta_carpeta)


if __name__ == '__main__':
    hasRun = False
    # Crear una carpeta llamada "audio" si no existe
    carpeta_destino = 'audio'
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    to0grados()
    # GPIO.output(empujeFan, GPIO.LOW)
    time.sleep(5)
    mic_configurado = configurar_mic()
    GPIO.output(pinSuccionador, GPIO.LOW)
    try:
        while not hasRun:
            print('-------Inicio Ciclo')
            to0grados()
            #compuertaAbierta()  # Se mantiene abierto siempre que no haya mosquitos dentro del seleccionador
            GPIO.output(pinSuccionador, GPIO.LOW)
            deteccionMosquito() #No pasa de esta linea hasta que entre un mosquito
            #Se a detectado un mosquito se procede a cerrar las compuertas.
            #compuertaCerrado()
            #Se espera detectar dentro de la capsula
            #deteccionMosquitoDentroDeLaCapsula()#Una vez detectado continua con el flujo
            gradosPosicion(grados * 1)#Se posiciona en la posicion en donde se encuentra el microfono para la deteccion
            print("Para el succionador")
            GPIO.output(pinSuccionador, GPIO.HIGH)
            print('Se procede a la clasificacion del mosquito')
            # Configurar el microfono fuera de la funcion
            # Ejecutar el detector de frecuencia con la configuracion del microfono
            compuertaPosicion=0
            estadoDeteccion=False
            while not estadoDeteccion:
                resultado = detectar_frecuencia_usb(mic_configurado)
                compuertaPosicion=selectorCompuertaByRangoFrecuencia(resultado[0],500, 630, 1,compuertaPosicion)
                compuertaPosicion=selectorCompuertaByRangoFrecuencia(resultado[0],630, 800, 2,compuertaPosicion)
                if compuertaPosicion != 0:
                    GPIO.output(pinSuccionador, GPIO.LOW)#Se activa el succionador
                    time.sleep(1)
                    gradosPosicion(grados * 1) #Se mueve a la posicion de la camara verificar esto/////////
                    GPIO.output(pinSuccionador, GPIO.HIGH)#Paramos el succionador para sacarle una foto
                    time.sleep(2)
                    # Obtener la fecha y hora actual
                    fecha_hora_actual = datetime.datetime.now()
                    # Formatear la fecha y hora como una cadena
                    formato_fecha_hora = fecha_hora_actual.strftime("%Y-%m-%d_%H-%M-%S")
                    # Generar el nombre de archivo dentro de la carpeta "audio"
                    nombre_archivo = os.path.join(carpeta_destino, 'Mosquito:' + str(
                        compuertaPosicion) + 'fecha:' + formato_fecha_hora + '.wav')
                    # Guardar la señal procesada en un archivo de audio WAV
                    datos_np = np.frombuffer(resultado[1], dtype=np.int16)
                    guardar_datos(compuertaPosicion,datos_np,frecuencia_muestreo)
                    print('Se guarda la imagen del mosquito y el audio')
                    #---------Se guarda el audio y la imagen------
                    GPIO.output(pinSuccionador, GPIO.LOW)#Volvemos a activar el succionador para mover
                    time.sleep(2)
                    print(f'Se detecto el tipo de mosquito para la compuerta:{compuertaPosicion}')
                    gradosPosicion(grados * compuertaPosicion)
                    to90grados()
                    time.sleep(5)
                    GPIO.output(pinSuccionador, GPIO.HIGH) #Apagamos el succionar mientras
                    retorno(grados * (compuertaPosicion+2))
                    compuertaPosicion = 0
                    estadoDeteccion=True

    except KeyboardInterrupt:
        c.stop()
        GPIO.cleanup()
        print("Cleanup gpio")
        # hasRun=True
        print("Stop motor")
        # GPIO.output(succionFan, GPIO.LOW)
        for pin in StepPins:
            GPIO.output(pin, False)
