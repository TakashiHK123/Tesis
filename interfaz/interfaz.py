# import kivy
# from progPrueba import ejemplo as pP
#from ProgParaInterfaz import mainPPI as pP
#from ProgParaInterfaz2 import mainPPI as pP
from ProgOpi3b import mainPPI as pP
if __name__ == '__main__': #tuve que hacer esto para que no se abra una segunda ventana de kivy al ejecutar el Process,
                           # segun lo que lei en linux no deberia ser necesario, solo en windows

    from kivy.app import App
    from kivy.uix.widget import Widget
    # from kivy.uix.button import Button
    from kivy.properties import StringProperty,NumericProperty,BooleanProperty,ObjectProperty
    #from kivy.uix.gridlayout import GridLayout
    #from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.boxlayout import BoxLayout
    from random import randint
    from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
    import matplotlib.pyplot as plt
    from kivy.uix.screenmanager import ScreenManager, Screen 
    from kivy.lang import Builder
    from kivy.clock import Clock
    from multiprocessing import Process, Queue, Event
    #from kivy.config import Config
    from kivy.core.window import Window
    import cv2
    from kivy.graphics.texture import Texture
    import numpy as np
    import librosa
    import librosa.display
    import time
    import os


    try:
        img=cv2.imread("interfaz/tinky.jpeg")
        buf1 = cv2.flip(img, 0)
        buf = buf1.tobytes()#tostring()
        image_texture = Texture.create(
        size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
    except:
        image_texture=None

    plt.style.use("dark_background")

    class FirstWindow(Screen):
        pass

    class SecondWindow(Screen):
        pass

    class WindowManager(ScreenManager):
        pass

    class Innterfaz(App):
        pCorriendo=BooleanProperty(False)
        botonScript=StringProperty("Iniciar Script")
        #imagen=StringProperty("")#"tinky.jpeg")
        contM=NumericProperty(0)
        contH=NumericProperty(0)
        contMix=NumericProperty(0)
        contNada=NumericProperty(0)
        estado = StringProperty('Trampa\nApagada')
        modoManual =BooleanProperty(True)
        frecD=NumericProperty(0)
        compuerta=NumericProperty(1) #3 indefinido 2 macho 1 hembra
        error=StringProperty("")
        ocupado=BooleanProperty(False)
        video=BooleanProperty(False)
        foto=BooleanProperty(False)
        grabando=BooleanProperty(False)
        tipoDeGrafico=NumericProperty(2)
        texture=ObjectProperty(image_texture)
        rangoH =BooleanProperty(0)
        rangoM =BooleanProperty(0)

        

        def graficar(self):
            self.borrarGrafico() # si no pongo esto se acumlan graficos encimados
            self.box = BoxLayout(pos=(0,0.01),size_hint=(.8, .6))
            self.box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
            self.root.get_screen('first').add_widget(self.box)

        def borrarGrafico(self):
            try:
                self.root.get_screen('first').remove_widget(self.box)
            except:
                pass #xd
        
        def mensajeError(self):
            a=self.error.split("\n")
            self.error="\n".join(a[-4:])

        def checkQueue(self,dt=0):
            if not self.qEnt.empty():
                A=self.qEnt.get()
                if A=="Espectrograma" or A=="ADC":
                    x=np.array(self.qEnt.get(),dtype=np.float32)
                    plt.clf()
                    if A=="ADC":
                        sr=3750
                    else:
                        sr=44100
                    if self.tipoDeGrafico==2 or A=="ADC":
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
                        magMin=spectrogram_db.min()
                        if A=="ADC":
                            offset=35
                            ruido=824
                            spectrogram_db[np.where(~(((freqs >= min_freq ) & (freqs<=(824-offset))) | ((freqs <= max_freq) & (freqs>=(824+offset)) )))[0]]=magMin
                        else:
                            spectrogram_db[np.where(~((freqs >= min_freq ) & (freqs <= max_freq)))[0]]=magMin
                        librosa.display.specshow(spectrogram_db,sr=sr, hop_length=hop_length, x_axis='time', y_axis='log')
                        plt.ylim([min_freq, max_freq])
                        plt.title('Espectrograma')
                        plt.colorbar(format='%+2.0fdb')
                        plt.tight_layout()
                        if A=="ADC":
                            freqMachos=np.where((freqs >=700) & (freqs <= 1050))[0]
                            freqHembras=np.where((freqs >=450) & (freqs <=650))[0]
                            for i in spectrogram_db[freqMachos, :]:
                                if i.max()>-7:
                                    self.rangoM=1
                                    break
                            for i in spectrogram_db[freqHembras, :]:
                                if i.max()>-5:
                                    self.rangoH=1
                                    break

                    else:
                        plt.specgram(x,NFFT=1024,Fs=44100)
                        plt.xlabel('Tiempo (s)')
                        plt.ylabel('Frecuencia (Hz)')
                        plt.ylim(0, 3000)
                    
                    self.graficar()



                elif A=="Graficar":
                    y=self.qEnt.get()
                    x=self.qEnt.get()
                    freqAltas=self.qEnt.get()
                    indices=self.qEnt.get()
                    self.frecD=int(max(freqAltas))
                    plt.clf()
                    plt.plot(x,y)
                    #plt.figure(figsize=(8, 4))
                    plt.xlabel('Frecuencia (Hz)')
                    plt.ylabel('Magnitud')
                    plt.title('Espectro de Magnitud')
                    plt.plot(freqAltas, y[indices], 'ro', markersize=5)
                    plt.xlim(0, 3000)
                    #plt.grid(True)
                    direccion=self.qEnt.get()
                    if not(direccion is None):
                        plt.savefig(direccion)
                    self.graficar()
                elif A=="NuevoEstado":
                    x=self.qEnt.get()
                    self.estado=x
                    if x=="Fotografiando":
                        self.qSal.put("Compuerta")
                        self.qSal.put(self.compuerta)
                    if x=="Clasificando\nMosquito":
                        if self.rangoH and self.rangoM:
                            self.contMix+=1
                        elif self.rangoH:
                            self.contH+=1
                        elif self.rangoM:
                            self.contM+=1
                        else:
                            self.contNada+=1
                        self.rangoH=0
                        self.rangoM=0
                elif A=="Imagen":
                    frame=self.qEnt.get()
                    if type(frame)==np.ndarray:
                        #print(type(frame))
                        buf1 = cv2.flip(frame, 0)
                        buf = buf1.tobytes()#tostring()
                        image_texture = Texture.create(
                        size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                        self.texture=image_texture
                    else:
                        self.error+="Error con la imagen\n"
                        self.mensajeError()
                        
                    
                elif A=="FinAccion":
                    self.ocupado=False

                elif A=="video":
                    self.cap = cv2.VideoCapture(0)
                    if not self.cap.isOpened():
                        self.error+="Error con la camara\n"
                        self.mensajeError()
                        print("Error: No se puede acceder a la cámara. ¿Está conectada correctamente?")
                        self.qSal.put("Error")
                        self.ocupado=False
                    else:
                        self.video=True
                        Clock.schedule_interval(self.videoCapture, 1.0/20)
                
                elif A=="pararVideo":
                    self.pararVideo()

                elif A=="cierrePorError":
                    self.pararPrograma()
                    self.error+="Error en el Script\n"
                    self.mensajeError()


        def pararVideo(self):
            Clock.unschedule(self.videoCapture)
            self.cap.release()
            cv2.destroyAllWindows()
            self.ocupado=False
            self.video=False
            self.foto=False
            if self.grabando:
                self.pararGrabacion()

        def guardarImagen(self):
            cv2.imwrite("carpeta_pruebas\myfile.jpg",self.frame)
            self.foto=False
        
        def grabarVideo(self):
            #self.grabacion = cv2.VideoWriter('videoSalida.avi',cv2.VideoWriter_fourcc(*'XVID'),20.0,(640,480))
            self.grabacion = cv2.VideoWriter('videoSalida.mp4', cv2.VideoWriter_fourcc(*'MP4V'), 20.0, (640,480))
            self.grabando = True

        def pararGrabacion(self):
            try:
                self.grabacion.release()
            except:
                pass

            self.grabando = False

        def videoCapture(self,dt=0):
            if not self.foto:
                ret, self.frame = self.cap.read()
                if not ret:
                    print("Error al leer el fotograma")
                    return
                buf1 = cv2.flip(self.frame, 0)
                buf = buf1.tobytes()#.tostring()
                image_texture = Texture.create(
                    size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture=image_texture
                if self.grabando==True:
                    self.grabacion.write(self.frame)


        def iniciarPrograma(self):
            if self.pCorriendo:
                self.pararPrograma()
            else:
                self.pCorriendo=1
                self.ocupado=False
                self.qEnt=Queue() 
                self.qSal=Queue() 
                self.cerrar=Event()
                self.p=Process(target=pP,args=(self.qEnt,self.qSal,self.cerrar))
                self.p.start()

                self.botonScript="Cerrar Script"
                self.qSal.put(["Modo Automatico","Modo Manual"][self.modoManual])
                Clock.schedule_interval(self.checkQueue, 1.0/5)

        def pararPrograma(self):
            if self.video:
                self.pararVideo()
                
            Clock.unschedule(self.checkQueue)
            # self.p.terminate()
            self.cerrar.set()
            tiempo=time.time()
            aux=0
            while(self.cerrar.is_set()):
                if time.time()-tiempo >10:
                    aux=1
                    break
            while (not self.qEnt.empty()):
                #self.checkQueue()
                self.qEnt.get()
            while (not self.qSal.empty()):
                self.qSal.get()
            if aux:
                self.p.kill()
                self.qEnt.close()
                self.qSal.close()
                self.error+="Cierre Forzdo (+10s)\n"
                self.mensajeError()
            else:
                self.qEnt.close()
                self.qSal.close()
                self.p.join(1)
                if self.p.is_alive():
                    #self.p.terminate()
                    self.p.kill()
                    print("error al cerrar")
                    self.error+="Error al cerrar\n"
                    self.mensajeError()
            self.pCorriendo=0
            self.estado='Trampa\nApagada'
            self.botonScript="Iniciar Script"

        def on_start(self):
            pass

        def on_stop(self):
            if self.pCorriendo:
                self.pararPrograma() 

        def build(self):
            return Builder.load_file('interfaz.kv')


if __name__ == '__main__':
    # Config.set('graphics', 'resizable', '0')
    # Config.set('graphics', 'width', '480')
    # Config.set('graphics', 'height', '320')
    #Window.size = (480, 320)
    #Window.fullscreen = True
    Window.maximize()
    #os.system("xrandr --output HDMI-1 --mode 720x480")
    Innterfaz().run()

