#!/usr/bin/env python
# -*- coding: utf-8 -*-
# libraries
import wiringpi
from wiringpi import GPIO
import numpy as np
import alsaaudio
import time
import os
import json
import threading
import librosa
import librosa.display
from scipy.signal import butter,filtfilt
import matplotlib.pyplot as plt
import wave


def mainPPI(queueSal,queueEnt,cierre,turbina,variablesCompartidas):
    ############################################
    plt.style.use("dark_background")
    plt.rc('font', size=12)          # controls default text sizes
    plt.rc('axes', titlesize=16)     # fontsize of the axes title
    plt.rc('axes', labelsize=16)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=14)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=13)    # fontsize of the tick labels
    ConfigFile="interfaz/configfile.json"
    with open(ConfigFile, 'r') as file:
        # Load the JSON data from the file
        json_data = json.load(file)

    wiringpi.wiringPiSetup()
    
    #Posiciones
    PosicionEntrada=json_data["Posiciones"][0]
    PosicionCamara=json_data["Posiciones"][1]
    PosicionInfrarrojo=json_data["Posiciones"][2]
    PosicionMicrofono=json_data["Posiciones"][3]
    PosicionSalida=json_data["Posiciones"][4]
    PosicionSalidaMachos=json_data["Posiciones"][5]
    PosicionSalidaHembras=json_data["Posiciones"][6]

    #ADC
    SCLK = 25
    MISO = 22
    MOSI = 23
    DRDY = 20
    CS2 = 19

    #Turbina para succion y expulsion
    PWM_ESC=21
    wiringpi.pinMode(PWM_ESC, GPIO.PWM_OUTPUT)
    wiringpi.pwmWrite(PWM_ESC,0)
    wiringpi.pwmSetRange(PWM_ESC,240000) #PWM frequency is 24000000 / (Clock * Range) = 50Hz.
    wiringpi.pwmSetClock(PWM_ESC, 2)

    def turbinaPWM(dutyCycle): # Duty cycle en micro segundos (us)
        global estadoTurbina
        estadoTurbina=dutyCycle
        dutyCycle=int(dutyCycle*12.0)
        wiringpi.pwmWrite(PWM_ESC,dutyCycle) #Duty cycle = x/Range (%) , x<range
    
    neutroPWM=1485
    def succionMinPWM():
        return turbina[0]
    def succionMaxPWM():
        return turbina[1]
    def expulsionPWM():
        return turbina[2]

    turbinaPWM(neutroPWM)
    
    #Encoder magnetico
    DEVICE_AS5600 = 0x36
    fd = wiringpi.wiringPiI2CSetupInterface("/dev/i2c-2",DEVICE_AS5600)
        
    def ReadRawAngle(): # Read angle (0-360 represented as 0-4096)
        read_bytes = (wiringpi.wiringPiI2CReadReg8(fd, 0x0C) & 31)<<8
        read_bytes+= wiringpi.wiringPiI2CReadReg8(fd, 0x0D) #0000 1111 1111 1111
        return ( read_bytes* 360.0) / 4096.0   
    
    posicionesAng={-1: 245.3, 0: 289.6, 1: 336.5, 2: 19.9+360, 3: 65.96+360, 4: 110.5+360, 5: 155.1+360, 6: 200.3+360, "prohibido":220}

    def Angulo():
        ang=ReadRawAngle()
        if ang<posicionesAng["prohibido"]:
            return ang+360
        return ang
    
    #stepper
    microsteps=16
    StepsPerRev=200*microsteps
    global posActual
    posActual=None
    wiringpi.wiringPiSetup()
    ENABLE=24
    STEP=26
    DIR=27
    ENDSTOP=13

    wiringpi.pinMode(ENDSTOP, GPIO.INPUT)
    wiringpi.pinMode(ENABLE, GPIO.OUTPUT)
    wiringpi.pinMode(STEP, GPIO.OUTPUT)
    wiringpi.pinMode(DIR, GPIO.OUTPUT)

    def setVel(vel):#grados/segundo
        global Tus #tiempo en microsegundos
        Tus=int(1/(vel/360*(StepsPerRev))*500000)

    setVel(60)

    def step(n=1,direction=True):
        wiringpi.digitalWrite(DIR, direction)
        for j in range(n):
            wiringpi.digitalWrite(STEP, True)
            wiringpi.delayMicroseconds(Tus)
            wiringpi.digitalWrite(STEP, False)
            wiringpi.delayMicroseconds(Tus)
            if variablesCompartidas["MosquitosEnLaTrampa"]>0:
                turbinaPWM(succionMinPWM())
            if cierre.is_set():
                raise KeyboardInterrupt('cierre detectado')
            

    def goToPos(pos=0,encoder=1): 
        NuevoEstado("Cámara en movimiento")   
        global posActual
        if (pos==posActual and not encoder) or pos>6 or pos <-1:
            return
        wiringpi.digitalWrite(ENABLE, False)
        wiringpi.delay(200)
        if encoder:
            obj=posicionesAng[pos]
            ang=Angulo()
            while(abs(ang-obj)>0.5):
                direction=ang>obj
                step(4,direction)
                ang=Angulo()
        else:
            if posActual==None:
                direction=True
                pos=0
            else:
                direction= posActual>pos
                dif=abs(posActual-pos)
            if pos==0:
                wiringpi.digitalWrite(DIR, direction)
                if not wiringpi.digitalRead(ENDSTOP):
                    step(50,0)
                for i in range(StepsPerRev):
                    if not wiringpi.digitalRead(ENDSTOP): 
                        if direction:
                            step(16)
                        else:
                            step(34,0)
                        break
                    step(1,direction)
            else:
                step(int(dif*400),direction)

        posActual=pos
        NuevoEstado("Posición alcanzada")
        wiringpi.delay(200)
        wiringpi.digitalWrite(ENABLE, True)

    #ADC
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
        
    #Deteccion de entrada de mosquitos al sistema
    def deteccionMosquito():
        
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
            turbinaPWM(succionMaxPWM())
            while(wiringpi.digitalRead(DRDY)):
                pass
            out=leerADC()
            if out>threshold or out<-threshold:
                
                SDATAC()
                wiringpi.digitalWrite(CS2, True)
                wiringpi.pinMode(SCLK, GPIO.INPUT)
                wiringpi.pinMode(MOSI, GPIO.INPUT)
                wiringpi.pinMode(CS2, GPIO.INPUT)
                variablesCompartidas["MosquitosEnLaTrampa"]+=1
                return True
            while(not wiringpi.digitalRead(DRDY)):
                pass

    def Opt101ADC(t=10):
        #t=10#s
        os.system("./interfaz/leerADC " +str(3750*t))
        l=[]
        with open("interfaz/datosADCinterfaz.txt","r") as a:
            for line in a:
                l.append(float(line))
        # variablesCompartidas["ADC"] =  np.array(l)
        global ADCdata
        ADCdata=np.array(l)
        # graficar("ADC")

    def Audio(duracion=10):
        CHANNELS = 1
        RATE = 44100
        CHUNK = 512
        try:
            cont=0
            for i in alsaaudio.cards():
                if i== 'HIDMediak':
                    cardindex=cont
                    break
                cont+=1
            stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, cardindex=cardindex)
        except:
            queueSal.put("error")
            queueSal.put("No hay Microfono")
            return 0
        stream.setchannels(CHANNELS)
        stream.setrate(RATE)
        stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        stream.setperiodsize(CHUNK)

        print("Grabando...")

        frames = []
        data = []

        for i in range(0, int(RATE / CHUNK * duracion)):
            if cierre.is_set():
                raise KeyboardInterrupt('cierre detectado')
            length, audio_data = stream.read()
            frames.append(audio_data)
            data.extend(np.frombuffer(audio_data, dtype=np.int16))

        print("Fin de la grabación.")
        stream.close()
        # variablesCompartidas["Audio"]=frames

        wf = wave.open(f"interfaz/wavtemp.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes para formato PCM_FORMAT_S16_LE
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

        #variablesCompartidas["AudioGraf"]=np.array(data,dtype=np.float32)
        global AudioData
        AudioData=np.array(data,dtype=np.float32)
        # graficar("Audio")
        return 1
    
    def graficar(A):
        if A=="Audio+Infrarrojo":
            A="ADC"
        fc_low = 250   # Lower cutoff frequency in Hz
        fc_high = 1200 # Upper cutoff frequency in Hz
        if A=="ADC":
            plt.figure(1)
            sr=3750
            # x=variablesCompartidas["ADC"][1:]
            x=ADCdata[1:]
        else:
            plt.figure(2)
            sr=44100
            # x=variablesCompartidas["AudioGraf"]  
            x=AudioData
        plt.clf()

        if A=="ADC":
            nyquist = 0.5 * sr
            low = fc_low / nyquist
            high = fc_high / nyquist
            b, a = butter(6, [low, high], btype='band')
            x = filtfilt(b, a, x)
        
            #b, a = butter(7, [820/ nyquist, 830/ nyquist], btype='bandstop')
            #x = filtfilt(b, a, x)
        
        if A=="ADC":
            n_fft=512
        else:
            n_fft=8192
        hop_length = n_fft // 4
        min_freq=300
        max_freq=1200
        spectrogram = librosa.stft(x, n_fft=n_fft, hop_length=hop_length,center=False)
        spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram))
        freqs = librosa.fft_frequencies(sr=sr, n_fft=spectrogram.shape[0] * 2 - 1)
        
        librosa.display.specshow(spectrogram_db,sr=sr, hop_length=hop_length, x_axis='time', y_axis='linear')
        plt.ylim([min_freq, max_freq])
        if A=="ADC":
            plt.title('Espectrograma de señal infrarroja')
        else:
            plt.title('Espectrograma de audio')
        
        plt.colorbar(format='%+2.0fdb')
        plt.tight_layout()
        if A=="ADC":
            rangoH=0
            rangoM=0
            Hmin=400
            Hmax=600
            Mmin=700
            Mmax=900
            freqMachos=np.where((freqs >=Mmin) & (freqs <= Mmax))[0]
            freqHembras=np.where((freqs >=Hmin) & (freqs <=Hmax))[0]
            for i in spectrogram_db[freqMachos, :]:
                if i.max()>=-15:
                    rangoM=1
                    break
            for i in spectrogram_db[freqHembras, :]:
                if i.max()>=-13:
                    rangoH=1
                    break
            if rangoH==rangoM: # 0y0 o 1y1
                variablesCompartidas["Salida"]=0
            elif rangoH==1:
                variablesCompartidas["Salida"]=1
            elif rangoM==1:
                variablesCompartidas["Salida"]=2
            variablesCompartidas["rangoH"]=rangoH
            variablesCompartidas["rangoM"]=rangoM

        if A=="ADC":
            plt.savefig("interfaz/ADCtemp.png")
            # variablesCompartidas["graficoADC"]=plt.gcf()
        if A=="Audio":
            plt.savefig("interfaz/Audiotemp.png")
            # variablesCompartidas["graficoAudio"]=plt.gcf()

    def NuevoEstado(texto):
        queueSal.put("NuevoEstado")
        queueSal.put(texto)
    #######################################
    
    global Accion
    global uAccion
    Accion=None
    uAccion=None
    def finAccion():
        global Accion
        global uAccion
        uAccion=Accion
        Accion=None
        queueSal.put("FinAccion")
    def revisarEnt():
        global Accion
        global uAccion
        if cierre.is_set():
            raise KeyboardInterrupt('cierre detectado')
        if not queueEnt.empty():
            A=queueEnt.get()
            Accion=A
        return 0

    NuevoEstado("Iniciando") 
    time.sleep(3.5)

    try:
        goToPos()
        NuevoEstado("Posicion Inicial")
        while True:
            revisarEnt()
            if variablesCompartidas["MosquitosEnLaTrampa"]>0:
                turbinaPWM(succionMinPWM())

            if Accion=="Posicion Inicial":
                
                goToPos(PosicionEntrada)
                    
                turbinaPWM(succionMaxPWM())
                NuevoEstado("Detectando\nMosquitos")
                if(deteccionMosquito()):  # No pasa de esta linea hasta que entre un mosquito
                    NuevoEstado("Mosquitos\nDetectados")
                    #wiringpi.delay(100)
                    turbinaPWM(succionMinPWM())   
                else:
                    revisarEnt()
                    turbinaPWM(neutroPWM)   
                finAccion()

            if Accion=="Audio" or Accion=="ADC" or Accion=="Audio+Infrarrojo":
                
                if variablesCompartidas["MosquitosEnLaTrampa"]>0:
                    turbinaPWM(succionMinPWM())
                if Accion=="Audio" or Accion=="Audio+Infrarrojo":
                    goToPos(PosicionMicrofono)
                else:
                    goToPos(PosicionInfrarrojo)
                print("Para el succionador")
                turbinaPWM(neutroPWM)
                time.sleep(1)
                    
                if Accion=="Audio":
                    NuevoEstado("Grabando\nSonido")
                    if Audio():
                        graficar("Audio")
                        queueSal.put("Audio")

                elif Accion=="ADC":
                    NuevoEstado("Leyendo\nADC")
                    Opt101ADC()
                    graficar("ADC")
                    queueSal.put("ADC")
                
                elif Accion=="Audio+Infrarrojo":
                    NuevoEstado("Grabando\nSonido y señal infrarroja")
                    t = threading.Thread(target=Opt101ADC)
                    t.daemon = True
                    t.start()
                    k=Audio()
                    t.join()
                    graficar("ADC")
                    if k:
                        graficar("Audio")
                        queueSal.put("Audio+Infrarrojo")
                    else:
                        queueSal.put("ADC")
                NuevoEstado("Medición completada")
                
                if variablesCompartidas["MosquitosEnLaTrampa"]>0:
                    turbinaPWM(succionMinPWM())
                finAccion()

            if Accion=="Soltar Mosquito":

                NuevoEstado("Clasificando\nMosquitos")
                if variablesCompartidas["MosquitosEnLaTrampa"]>0:
                    turbinaPWM(succionMinPWM())
                if variablesCompartidas["Salida"]==0:    
                    goToPos(PosicionSalida)
                elif variablesCompartidas["Salida"]==1:
                    goToPos(PosicionSalidaHembras)
                elif variablesCompartidas["Salida"]==2:
                    goToPos(PosicionSalidaMachos)
                turbinaPWM(expulsionPWM())
                NuevoEstado("Liberando Mosquitos")
                aux=time.time()
                while(time.time()-aux<10):
                    if cierre.is_set():
                        raise KeyboardInterrupt('cierre detectado')
                    turbinaPWM(expulsionPWM())
                variablesCompartidas["MosquitosEnLaTrampa"]=0
                turbinaPWM(neutroPWM)
                finAccion()
                NuevoEstado("Mosquitos liberados")
                
            
            if Accion=="Agitar":
                finAccion()
                
            
            if Accion=="video": #no es solo video, es todo lo relacionado a la camara
                
                if variablesCompartidas["MosquitosEnLaTrampa"]>0:
                    turbinaPWM(succionMinPWM())
                goToPos(PosicionCamara)

                NuevoEstado("En Posición de la cámara")
                
                uAccion=Accion
                Accion=None

                queueSal.put("video")
                while(not cierre.is_set()):
                    if variablesCompartidas["Turbina+Camara"] and variablesCompartidas["MosquitosEnLaTrampa"]>0:
                        turbinaPWM(succionMinPWM())
                    else:
                        turbinaPWM(neutroPWM)
                    if not queueEnt.empty():
                        kk=queueEnt.get()
                        if kk=="camaraPrendida":
                            continue 
                        elif kk=="pararVideo":
                            queueSal.put("pararVideo")
                        break
                if variablesCompartidas["MosquitosEnLaTrampa"]>0:
                    turbinaPWM(succionMinPWM())
            
            if Accion=="Infrarrojo+Video":
                if variablesCompartidas["MosquitosEnLaTrampa"]>0:
                    turbinaPWM(succionMinPWM())
                goToPos(PosicionCamara)

                NuevoEstado("Grabando video y señal infrarroja")
                turbinaPWM(neutroPWM)
                queueSal.put("videoyadc")
                ok=1
                while(not cierre.is_set()):
                    if not queueEnt.empty():
                        kk=queueEnt.get()
                        if kk=="pararVideo":
                            queueSal.put("pararVideo")
                        elif kk=="Error":
                            ok=0     
                        elif kk=="camaraPrendida":
                            ok=1
                            time.sleep(1)
                            queueSal.put("Infrarrojo+Video1")                       
                        break
                if cierre.is_set():
                    ok=0
                if ok:
                    Opt101ADC()
                    queueSal.put("pararVideo")
                    graficar("ADC")
                    queueSal.put("Infrarrojo+Video")
                NuevoEstado("Grabación completada")
                finAccion()




    except: #Exception as e:# KeyboardInterrupt:
        #print(e) 
        wiringpi.pinMode(STEP, GPIO.INPUT)
        wiringpi.pinMode(DIR, GPIO.INPUT)
        wiringpi.pinMode(ENABLE, GPIO.INPUT)
        wiringpi.pinMode(PWM_ESC, GPIO.INPUT)
        print("Cleanup gpio")

        if not cierre.is_set():
            queueSal.put("cierrePorError")
            while not cierre.is_set():
                pass
        cierre.clear()
            