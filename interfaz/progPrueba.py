import random
import time
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2 
import sys
import librosa
import librosa.display
from scipy.signal import butter,filtfilt

#import signal

# def handle_exit(sig, frame):
#     raise(SystemExit)

plt.style.use("dark_background")
plt.rc('font', size=12)          # controls default text sizes
plt.rc('axes', titlesize=16)     # fontsize of the axes title
plt.rc('axes', labelsize=16)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=14)    # fontsize of the tick labels
plt.rc('ytick', labelsize=13)    # fontsize of the tick labels

  

print("programa")

aa="holaaaa"

def prueba1():
    print("puebaaa")

class FakeClass():
    def __init__(self) -> None:
        pass
    def put(self,a=0):
        pass
    def get(self,a=0):
        pass
    def is_set(self):
        pass
    def empty(self):
        return True
    def clear(self):
        pass


#plt.plot([1,1.2],[4,5])

def ejemplo(queueSal=FakeClass(),queueEnt=FakeClass(),cierre=FakeClass(),turbina=[1,2,3],variablesCompartidas={}):
    # signal.signal(signal.SIGTERM, handle_exit)  #probar en linux, en windows no funciona
    # signal.signal(signal.SIGINT, handle_exit)
    def _graficar(A):
        if A=="Audio+Infrarrojo":
            A="ADC"
        fc_low = 250   # Lower cutoff frequency in Hz
        fc_high = 1200 # Upper cutoff frequency in Hz
        if A=="ADC":
            plt.figure(1)
            sr=3750
            x=variablesCompartidas["ADC"][1:]
        else:
            plt.figure(2)
            sr=44100
            x=variablesCompartidas["AudioGraf"]  
        plt.clf()

        if A=="ADC":
            nyquist = 0.5 * sr
            low = fc_low / nyquist
            high = fc_high / nyquist
            b, a = butter(6, [low, high], btype='band')
            x = filtfilt(b, a, x)
        
            b, a = butter(7, [820/ nyquist, 830/ nyquist], btype='bandstop')
            x = filtfilt(b, a, x)
        
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
            variablesCompartidas["graficoADC"]=plt.gcf()
        if A=="Audio":
            variablesCompartidas["graficoAudio"]=plt.gcf()
    try:
        l=[]
        T=[]
        # with open("/content/drive/MyDrive/p4/deteccionDeFrecTrampa/sinnada.txt","r") as a:
        #with open("interfaz/medSoloHembras2.txt","r") as a:
        with open("interfaz/muchos_7.txt","r") as a:
        # with open("/content/drive/MyDrive/p4/deteccionDeFrecTrampa/medicionSoloMachos1.txt","r") as a:
            cont=0
            for line in a:
                try:
                    if not cont:
                        cont=1
                        tiempo=float(line)
                    else:
                        l.append(float(line))
                except:
                    pass
            """for line in a:
                try:
                    val , t=line.split(" ")
                    t=int(t)/1000000.0
                    #if True:#
                    if  t>=(0) and t<=(10):
                        val =float(val)
                        l.append(val)
                        T.append(t)
                except:
                    pass"""
        img = cv2.imread("interfaz/tinky.jpeg")
        #print(img[:10])
        #print(1)
        for i in img[10]:
            i[0]=0
            i[1]=254
            i[2]=0
        if not os.path.exists("carpeta_pruebas"):
            os.makedirs("carpeta_pruebas")
        archivo=os.path.join("carpeta_pruebas", 'myfile.jpg')
        # plt.plot([1,1.2],[4,5])
        # plt.savefig(archivo)
        #print(img)
        cv2.imwrite(archivo, img)
        #print(2)
        tiempo=time.time()
        #print("holaa")
        y=np.zeros(1024)
        x=np.zeros(1024)
        
        plt.figure(3)
        plt.plot([69,42],[42,69])
        
        
        queueSal.put("NuevoEstado")
        queueSal.put("Iniciando")
        #queueSal.put("Imagen")#eliminado
        #queueSal.put("datos\mosquitos1_2024-03-05_01-26-23\imagen.jpg")
        #queueSal.put(img)
        variablesCompartidas["ADC"]=l
        _graficar("ADC")
        queueSal.put('ADC')
        
        #queueSal.put(l)
        time.sleep(3)
        cambio=turbina[0]
        print(cambio)
        print(variablesCompartidas["MosquitosEnLaTrampa"])
        accion=None
        while(True):   
            # queueSal.put("Imagen")
            # queueSal.put(img)
            if turbina[0]!=cambio:
                cambio=turbina[0]
                print(cambio)
            if not queueEnt.empty():
                accion=queueEnt.get()
                print(accion)
                if accion!="video": queueSal.put("FinAccion")
            if accion=="video":
                accion=None
                queueSal.put("video")
                while(not cierre.is_set()):
                    if not queueEnt.empty():
                        #accion=queueEnt.get()
                        A=queueEnt.get()
                        if A=="camaraPrendida":
                            continue
                        if A=="pararVideo":
                            queueSal.put("pararVideo")
                        break

            if cierre.is_set():
                raise KeyboardInterrupt('kk')
            #time.sleep(2)
            # if time.time()-tiempo >5:
            #     print("nuevo grafico")
            #     for i in range(1024):
            #         y[i]=random.random()
            #         x[i]=i
            #     # queueSal.put("Graficar")
            #     # queueSal.put(y)
            #     # queueSal.put(x)
            #     # queueSal.put([500,400])
            #     # queueSal.put([40,80])
            #     # #queueSal.put("carpeta_pruebas\grafico.png")
            #     # queueSal.put(None)
            #     tiempo=time.time()
            #     # queueSal.put("Espectrograma")
            #     # queueSal.put(y)
            if __name__ == '__main__':
                break
            time.sleep(.5)
            for i in img[random.randint(200,500)]:
                i[0]=0
                i[1]=0
                i[2]=254
            try:
                #while(not cv2.imwrite(archivo, img)):
                #   print("error")
                cv2.imwrite(archivo, img)
            except:
                print("error2")
            #print(3)
            #queueSal.put("Imagen")
            #queueSal.put(img)
    except KeyboardInterrupt as e:
        print('exit handled')
        #queue.close()
        #cv2.destroyAllWindows()
        print(e)
        #time.sleep(5)
        cierre.clear()
        #return None
        #sys.exit()
        



if __name__ == '__main__':
    print("Main")
    ejemplo()