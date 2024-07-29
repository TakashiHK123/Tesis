#!/usr/bin/env python
# -*- coding: utf-8 -*-
# libraries
import wiringpi
from wiringpi import GPIO
# import RPi.GPIO as GPIO
import numpy as np
import scipy.io.wavfile as wav
import alsaaudio
import time
# import pyudev
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from scipy.io.wavfile import write
from datetime import datetime 
import os
import cv2
from collections import Counter
import wave
# import shutil



def mainPPI(queueSal,queueEnt,cierre):
    ############################################
    wiringpi.wiringPiSetup()
    
    tiempoDelay = 1.5  # El tiempo necesario para no detectar un falso negativo
    puertoCamara = 0
    puertoMicrofono = 2
    carpetaDatos = "datos"
    

    #ADC
    SCLK = 25
    MISO = 22
    MOSI = 23
    DRDY = 20
    CS2 = 19

    # Definir fan de succion y de empuje
    servoPIN = 21
    pinSuccionador = 17
    finalCarrera=2
    wiringpi.pinMode(finalCarrera, GPIO.INPUT)
    wiringpi.pullUpDnControl(finalCarrera,GPIO.PUD_UP)
    wiringpi.pinMode(servoPIN, GPIO.PWM_OUTPUT)
    wiringpi.pwmSetClock(servoPIN, 480)
    wiringpi.pwmWrite(servoPIN,25)
    # Define el número del pin GPIO que deseas usar
    #pin_sensor = 2
    # Configura el pin como entrada sensor
    #wiringpi.pinMode(pin_sensor, GPIO.INPUT)
    # Configura el pin para salida digital on/off para el succionador controlador por el relay
    wiringpi.pinMode(pinSuccionador, GPIO.OUTPUT)
    
    StepPins = [18,24,26,27]
    # Set all pins as output
    for pin in StepPins:
        print("Setup pins")
        wiringpi.pinMode(pin, GPIO.OUTPUT)
        wiringpi.digitalWrite(pin, False)

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
    # Define advanced normal sequence
    StepCount3 = 4
    Seq3 = []
    Seq3 = [i for i in range(0, StepCount2)]
    Seq3[0] = [1, 1, 0, 0]
    Seq3[1] = [0, 1, 1, 0]
    Seq3[2] = [0, 0, 1, 1]
    Seq3[3] = [1, 0, 0, 1]
    # Choose a sequence to use
    Seq = Seq3
    StepCount = StepCount3


    def to90grados():
        for angle9 in range(0, 115, 5):
            duty_cycle9 = 25 + (angle9 / 1.8)
            wiringpi.pwmWrite(servoPIN,int(duty_cycle9))
            wiringpi.delay(7)
        print("Valvula Expulsar")


    def to0grados():
        for angle0 in range(110, -1, -5):
            duty_cycle0 = 25 + (angle0 / 1.8)
            wiringpi.pwmWrite(servoPIN,int(duty_cycle0))
            wiringpi.delay(7)
        print("Valvula Succionar")


    def steps(nb,cierre=cierre):
        StepCounter = 0
        if nb < 0:
            sign = -1
        else:
            sign = 1
        nb = sign * nb * 2  # times 2 because half-step
        print("nbsteps {} and sign {}".format(nb, sign))
        for i in range(nb):
            if cierre.is_set():
                raise KeyboardInterrupt('cierre detectado')
            for pin in range(4):
                xpin = StepPins[pin]
                if Seq[StepCounter][pin] != 0:
                    wiringpi.digitalWrite(xpin, True)
                else:
                    wiringpi.digitalWrite(xpin, False)
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
    nbStepsPerRev = 2048/2
    grados = 45


    def grados_a_pasos(grados):
        pasos = (grados / 360) * nbStepsPerRev
        return int(pasos)


    def retorno(grados,cierre):
        """if (grados > 180):
            grados = 360 - grados
            steps(grados_a_pasos(grados),cierre)
        else:"""
        steps(-grados_a_pasos(grados),cierre)


    def gradosPosicion(grados,cierre):
        """if (grados > 180 and grados != 0):
            grados = 360 - grados
            steps(-grados_a_pasos(grados),cierre)
        el"""
        if (grados != 0):
            steps(grados_a_pasos(grados),cierre)
        print('Seleccionador en posicion')



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

    def seleccionADC():
        msg=0x510001 #default 0 positivo y 1 negativo
        for i in range(24):
            enviar(msg & 0x800000)
            msg = msg << 1
        wiringpi.delayMicroseconds(10)
    
    def seleccionSPS():
        msg=0x5300B0 #2k sps
        for i in range(24):
            enviar(msg & 0x800000)
            msg = msg << 1
        wiringpi.delayMicroseconds(10)
    
    def rdatac():
        #RDATAC
        msg = 0x03
        for i in range(8):
            enviar(msg & 0x80)
            msg = msg << 1
        wiringpi.delayMicroseconds(10)
    
    def SDATAC():
        #SDATAC: Stop Read Data Continuous
        msg = 0x0F
        while(wiringpi.digitalRead(DRDY)):
            pass
        for i in range(8):
            enviar(msg & 0x80)
            msg = msg << 1
    
    def leerADC():
        out=0x000000
        for	j in range(24):
            aux = recivir() & 0x000001
            aux = aux <<(23-j)
            out += aux
        signo=out & 0x800000
        out= out  & 0x7FFFFF
        if signo!=0:
            out = -(((~out) & 0x7FFFFF )+1)
        out=out/8388608*5.0
        return out
        

    def deteccionMosquito(queueSal,queueEnt,cierre):
        estado = 1
        
        wiringpi.pinMode(SCLK, GPIO.OUTPUT)
        wiringpi.pinMode(MOSI, GPIO.OUTPUT)
        wiringpi.pinMode(CS2, GPIO.OUTPUT)

        wiringpi.pinMode(MISO, GPIO.INPUT)
        wiringpi.pinMode(DRDY, GPIO.INPUT)

        wiringpi.digitalWrite(CS2, False)
        SDATAC()
        seleccionADC()
        seleccionSPS()
        rdatac()
        threshold=0.01 #volts
        while True:
            if cierre.is_set():
                SDATAC()
                wiringpi.digitalWrite(CS2, True)
                wiringpi.pinMode(SCLK, GPIO.INPUT)
                wiringpi.pinMode(MOSI, GPIO.INPUT)
                wiringpi.pinMode(CS2, GPIO.INPUT)
                raise KeyboardInterrupt('cierre detectado')
            if not queueEnt.empty():
                SDATAC()
                wiringpi.digitalWrite(CS2, True)
                wiringpi.pinMode(SCLK, GPIO.INPUT)
                wiringpi.pinMode(MOSI, GPIO.INPUT)
                wiringpi.pinMode(CS2, GPIO.INPUT)
                return False
            """if False:
                # Lee el valor del pin GPIO
                value = wiringpi.digitalRead(pin_sensor)
                if value == False:
                    if estado == 1:
                        tiempo_inicio = time.time()  # Inicia el temporizador
                        estado = 2
                    tiempo_baja = abs(time.time() - tiempo_inicio)
                    if tiempo_baja >= tiempoDelay:
                        print('Se procede a la deteccion del mosquito')
                        return True
                else:
                    estado = 1"""
            if True:
                while(wiringpi.digitalRead(DRDY)):
                    pass
                out=leerADC()
                if out>threshold or out<-threshold:
                    SDATAC()
                    wiringpi.digitalWrite(CS2, True)
                    wiringpi.pinMode(SCLK, GPIO.INPUT)
                    wiringpi.pinMode(MOSI, GPIO.INPUT)
                    wiringpi.pinMode(CS2, GPIO.INPUT)
                    return True
                while(not wiringpi.digitalRead(DRDY)):
                    pass

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
        except:# Exception as e:
            #print("Error:", e)
            return None  # Devuelve None si ocurre algún error durante el proceso de clasificación


    def capturar_foto(carpeta_fecha_hora,nombre):
        cap = cv2.VideoCapture(puertoCamara)  # Es el puerto donde se encuentra conectada la cámara web por USB
        # Verificar si la cámara está disponible
        if not cap.isOpened():
            print("Error: No se puede acceder a la cámara. ¿Está conectada correctamente?")
            queueSal.put("NuevoEstado")
            queueSal.put("Error: No se puede acceder a la cámara")
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
        queueSal.put("Imagen")
        queueSal.put(frame_maximo)
        return frame_maximo
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
        def record_and_analyze(self, filename,cola,save_plot_filename=None, input_device_index=None, repeat=False):
            while True:
                if input_device_index is None:
                    input_device_index = self.get_default_input_device_index()
                try:
                    stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, cardindex=2)
                except:
                    queueSal.put("NuevoEstado")
                    queueSal.put("No hay Microfono")
                    return None
                stream.setchannels(self.CHANNELS)
                stream.setrate(self.RATE)
                stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
                stream.setperiodsize(self.CHUNK)

                print("Grabando...")

                frames = []
                data = []

                for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                    if cierre.is_set():
                        raise KeyboardInterrupt('cierre detectado')
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
                cola.put("Graficar")
                cola.put(magnitude_spectrum[:len(fft_freq) // 2])
                cola.put(fft_freq[:len(fft_freq) // 2])
                cola.put(high_magnitude_freq)
                cola.put(high_magnitude_indices)
                # Visualización del espectro de magnitud
                # plt.figure(figsize=(8, 4))
                # plt.plot(fft_freq[:len(fft_freq) // 2], magnitude_spectrum[:len(fft_freq) // 2])
                # plt.xlabel('Frecuencia (Hz)')
                # plt.ylabel('Magnitud')
                # plt.title('Espectro de Magnitud')
                # plt.grid(True)

                # Resaltar las frecuencias que superan la magnitud de 0.2 dentro del rango de frecuencia especificado
                # plt.plot(high_magnitude_freq, magnitude_spectrum[high_magnitude_indices], 'ro', markersize=5)

                # plt.xlim(0, self.RATE / 15)  # Limitar la visualización a frecuencias positivas
                # plt.ylim(0, None)  # Limitar la visualización a magnitudes positivas

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
                    #plt.savefig(filename_plot)
                    cola.put(filename_plot)

                    # Guardar el archivo de audio dentro de la carpeta con la fecha y hora actual
                    filename_audio = os.path.join(carpeta_completa, filename)
                    os.makedirs(carpeta_completa, exist_ok=True)  # Crear la carpeta si no existe
                    os.rename(filename, filename_audio)
                    print("Se guardan los audios y imagen de la frecuencia")
                    self.LOCALDATE = subcarpeta_fecha
                else:
                    cola.put(None)
                # Imprimir las frecuencias que superan la magnitud de 0.2 dentro del rango de frecuencia especificado
                print("Frecuencias que superan la magnitud de 0.2 dentro del rango de 100 Hz a 1000 Hz:", high_magnitude_freq)
                return high_magnitude_freq
                if not repeat:
                    break

        def get_default_input_device_index(self):
            # Devuelve el primer índice de dispositivo
            return 2

        def Espectrograma(self,duracion=10):
            
            input_device_index = self.get_default_input_device_index()

            try:
                stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, cardindex=2)
            except:
                queueSal.put("NuevoEstado")
                queueSal.put("No hay Microfono")
                return None
            stream.setchannels(self.CHANNELS)
            stream.setrate(self.RATE)
            stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            stream.setperiodsize(self.CHUNK)

            print("Grabando...")

            frames = []
            data = []

            for i in range(0, int(self.RATE / self.CHUNK * duracion)):
                if cierre.is_set():
                    raise KeyboardInterrupt('cierre detectado')
                length, audio_data = stream.read()
                frames.append(audio_data)
                data.extend(np.frombuffer(audio_data, dtype=np.int16))

            print("Fin de la grabación.")
            stream.close()

            queueSal.put("Espectrograma")
            queueSal.put(data)

    """
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
            return None"""


    def apagarServo():
        wiringpi.pwmWrite(servoPIN,0)       
        print("apagar")
    def encenderServo():
        wiringpi.pwmWrite(servoPIN,110)

        
        
    
    
    
    
    
    #######################################
    global Modo
    Modo=queueEnt.get()
    print(Modo)
    global Accion
    Accion=None
    uAccion=None
    global PosicionActual
    PosicionActual=0
    detector = SoundDetector()
    global compuertaPosicion
    compuertaPosicion = 1
    def revisarEnt():
        global Accion
        global compuertaPosicion
        global Modo
        if cierre.is_set():
            raise KeyboardInterrupt('cierre detectado')
        if not queueEnt.empty():
            A=queueEnt.get()

            if A=="Modo Automatico" or A=="Modo Manual":
                Modo=A
                if A=="Modo Automatico":
                    Modo="Modo Automatico1"
                Accion=None
                uAccion=None
            elif A=="Compuerta":
                A=queueEnt.get()
                compuertaPosicion=A
                return 1
            else:
                Accion=A
        return 0
    def posAbsoluta(angulo):
        global PosicionActual
        if angulo>PosicionActual:
            gradosPosicion(angulo-PosicionActual,cierre)
        elif angulo<PosicionActual:
            retorno(PosicionActual-angulo,cierre)
        PosicionActual=angulo
    def posInicial():
        global PosicionActual
        while (not wiringpi.digitalRead(finalCarrera)):
            steps(-1)
        PosicionActual=0

    def succionar():
        encenderServo()
        time.sleep(1)
        to0grados()
        time.sleep(1)
        apagarServo()

    queueSal.put("NuevoEstado")
    queueSal.put("Trampa Encendida")
    #to0grados()
    succionar()
    posSuccionando=True
    time.sleep(2)
    wiringpi.digitalWrite(pinSuccionador, True)
    try:
        #posInicial()
        while True:
            revisarEnt()
            if Modo=="Modo Automatico" or Accion=="Posicion Inicial" or Modo=="Modo Automatico1":
                if Modo=="Modo Automatico1":
                    Modo="Modo Automatico"
                if uAccion!="Posicion Inicial":
                    succionar()
                    posSuccionando=True
                    wiringpi.digitalWrite(pinSuccionador, False)
                    posAbsoluta(0)
                    #posInicial()
                    print('-------Inicio Ciclo')
                    queueSal.put("NuevoEstado")
                    queueSal.put("Iniciando")
                    
                
                uAccion=Accion
                Accion=None
                
                # compuertaAbierta()  # Se mantiene abierto siempre que no haya mosquitos dentro del seleccionador
                wiringpi.digitalWrite(pinSuccionador, False)
                queueSal.put("NuevoEstado")
                queueSal.put("Detectando\nMosquitos")
                if(deteccionMosquito(queueSal,queueEnt,cierre)):  # No pasa de esta linea hasta que entre un mosquito
                    queueSal.put("NuevoEstado")
                    queueSal.put("Mosquito\nDetectado")
                    
                else:
                    revisarEnt()
                queueSal.put("FinAccion")
            if Modo=="Modo Automatico" or Accion=="Grabar Audio" or Accion=="Espectrograma" or Accion=="ADC":
                

                if not posSuccionando:
                    succionar()
                    posSuccionando=True
                if uAccion!="Grabar Audio" or uAccion!="Espectrograma" or uAccion!="ADC":
                    #gradosPosicion(grados * 1,cierre)  # Se posiciona en la posicion en donde se encuentra el microfono para la deteccion
                    wiringpi.digitalWrite(pinSuccionador, False)
                    posAbsoluta(grados * 1)
                    print("Para el succionador")
                    wiringpi.digitalWrite(pinSuccionador, True)
                    time.sleep(4)
                    print('Se procede a la clasificacion del mosquito')
                
                for pin in StepPins:
                    wiringpi.digitalWrite(pin, False)
                if  Accion=="Grabar Audio":
                    # Uso de la clase SoundDetector
                    queueSal.put("NuevoEstado")
                    queueSal.put("Grabando\nSonido")
                    high_magnitude_freq = None
                    
                    high_magnitude_freq = detector.record_and_analyze("grabacion.wav", save_plot_filename="spectrogram.png", input_device_index=2, repeat=False,cola=queueSal)  # Cambia el valor de input_device_index según tu dispositivo
                    print(high_magnitude_freq)
                    clasificacion = clasificar_frecuencia(high_magnitude_freq)
                    print(clasificacion)
                    
                elif Accion=="Espectrograma":
                    queueSal.put("NuevoEstado")
                    queueSal.put("Grabando\nSonido")
                    detector.Espectrograma()

                elif Modo=="Modo Automatico" or Accion=="ADC":
                    queueSal.put("NuevoEstado")
                    queueSal.put("Leyendo ADC")
                    os.system("./leerADC")
                    l=[]
                    with open("datosADCinterfaz.txt","r") as a:
                        for line in a:
                            l.append(float(line))
                    queueSal.put("ADC")
                    queueSal.put(np.array(l))
                queueSal.put("FinAccion")


                uAccion=Accion
                Accion=None


            if Modo=="Modo Automatico":
                if not posSuccionando:
                    succionar()
                    posSuccionando=True
                
                #if compuertaPosicion != 0:
                wiringpi.digitalWrite(pinSuccionador, False)  # Se activa el succionador
                time.sleep(3)
                posAbsoluta(grados*2)
                #gradosPosicion(grados * 1,cierre)  # Se mueve a la posicion de la camara verificar esto/////////
                wiringpi.digitalWrite(pinSuccionador, True)  # Paramos el succionador para sacarle una foto
                time.sleep(2)
                queueSal.put("NuevoEstado")
                queueSal.put("Fotografiando")
                while(not revisarEnt()):
                    pass
                
                if(detector.obtener_fecha_guardada() is not None):
                    fechaGuardada = detector.obtener_fecha_guardada()
                else:
                    fechaGuardada = "sinFecha"
                foto=capturar_foto(fechaGuardada,"MosquitoSinClasificar")
                
                print('Se guarda la imagen del mosquito')
                queueSal.put("FinAccion")

            if Modo=="Modo Automatico" or Accion=="Soltar Mosquito":
                
                
                if uAccion!="Soltar Mosquito":
                    queueSal.put("NuevoEstado")
                    queueSal.put("Clasificando\nMosquito")
                    wiringpi.digitalWrite(pinSuccionador, False)  # Volvemos a activar el succionador para mover
                    time.sleep(1)
                    #print(f'Se detecto el tipo de mosquito para la compuerta:{compuertaPosicion}')
                    #gradosPosicion(grados * compuertaPosicion,cierre)
                    posAbsoluta(grados*(-1))#2+compuertaPosicion
                    encenderServo()
                    to90grados()
                    posSuccionando=False

                uAccion=Accion
                Accion=None
                # ---------Se guarda el audio y la imagen------
                print(f'Se detecto el tipo de mosquito para la compuerta:{compuertaPosicion}')
                if Modo=="Modo Automatico":
                    time.sleep(10)
                    #retorno(grados * (compuertaPosicion + 2),cierre)
                    posAbsoluta(0)
                    wiringpi.digitalWrite(pinSuccionador, True)  # Apagamos el succionar mientras
                    #retorno(grados * (compuertaPosicion + 2))
                    #compuertaPosicion = 0
                    #estadoDeteccion = True
                queueSal.put("FinAccion")
            
            if Accion=="Agitar":
                wiringpi.digitalWrite(pinSuccionador, False)
                wiringpi.delay(1000)
                to0grados()
                wiringpi.delay(500)
                to90grados()
                wiringpi.delay(500)
                to0grados()
                wiringpi.delay(500)
                to90grados()
                wiringpi.delay(500)
                to0grados()
                if posSuccionando:
                    succionar()
                wiringpi.digitalWrite(pinSuccionador, True)
                wiringpi.delay(2000)
                Accion=None
                queueSal.put("FinAccion")
                
            
            if Accion=="video":
                if not posSuccionando:
                    succionar()
                    posSuccionando=True
                
                if uAccion!="video":
                    #if compuertaPosicion != 0:
                    wiringpi.digitalWrite(pinSuccionador, False)  # Se activa el succionador
                    time.sleep(3)
                    posAbsoluta(grados*2)
                    #gradosPosicion(grados * 1,cierre)  # Se mueve a la posicion de la camara verificar esto/////////
                    wiringpi.digitalWrite(pinSuccionador, True)  # Paramos el succionador para sacarle una foto
                    time.sleep(2)
                    queueSal.put("NuevoEstado")
                    queueSal.put("Camara Prendida")
                
                uAccion=Accion
                Accion=None

                queueSal.put("video")
                while(not cierre.is_set()):
                    if not queueEnt.empty():
                        if queueEnt.get()=="pararVideo":
                            queueSal.put("pararVideo")
                        break
            


    except: #Exception as e:# KeyboardInterrupt:
        #print(e)
        
        wiringpi.digitalWrite(pinSuccionador, True)
        for pin in StepPins:
            wiringpi.digitalWrite(pin, False)

        #for pin in StepPins:
        #    wiringpi.pinMode(pin, GPIO.INPUT)
        #wiringpi.pullUpDnControl(18,1)
        # wiringpi.pinMode(pinSuccionador, GPIO.INPUT)
        # wiringpi.pinMode(finalCarrera, GPIO.INPUT)
        wiringpi.pinMode(servoPIN, GPIO.INPUT)
        print("Cleanup gpio")

        print("Stop motor")
        # wiringpi.digitalWrite(succionFan, False)
        if not cierre.is_set():
            queueSal.put("cierrePorError")
            while not cierre.is_set():
                pass
        cierre.clear()
            

if __name__ == '__main__':
    mainPPI()
