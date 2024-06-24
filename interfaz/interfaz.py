# import kivy
from progPrueba import ejemplo as pP
#from ProgParaInterfaz import mainPPI as pP
#from ProgParaInterfaz2 import mainPPI as pP
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
        estado = StringProperty('Trampa\nApagada')
        modoManual =BooleanProperty(True)
        frecD=NumericProperty(0)
        error=StringProperty("")
        ocupado=BooleanProperty(False)
        video=BooleanProperty(False)
        foto=BooleanProperty(False)
        grabando=BooleanProperty(False)
        tipoDeGrafico=NumericProperty(0)
        texture=ObjectProperty(image_texture)

        

        def graficar(self):
            self.borrarGrafico() # si no pongo esto se acumlan graficos encimados
            self.box = BoxLayout(pos=(0,0),size_hint=(.8, .6))
            self.box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
            self.root.get_screen('first').add_widget(self.box)

        def borrarGrafico(self):
            try:
                self.root.get_screen('first').remove_widget(self.box)
            except:
                pass #xd
        
        def mensajeError(self):
            a=self.error.split("\n")
            self.error="\n".join(a[-5:])

        def checkQueue(self,dt=0):
            if not self.qEnt.empty():
                A=self.qEnt.get()
                if A=="Espectrograma":
                    x=self.qEnt.get()
                    plt.clf()

                    if self.tipoDeGrafico==2:
                        spectrogram = librosa.stft(x)
                        #plt.figure(figsize=(10, 5))
                        librosa.display.specshow(librosa.power_to_db(np.abs(spectrogram)**2), sr=44100, x_axis='time', y_axis='log')
                        #librosa.display.specshow(librosa.power_to_db(spectrogram), sr=44100, x_axis='time', y_axis='log')
                        plt.title('Espectrograma')
                        plt.colorbar(format='%+2.0fdb')
                        plt.tight_layout()
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
                    if x=="Clasificando\nMosquito":
                        if self.frecD>=550:
                            self.contH+=1
                        else:
                            self.contM+=1
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
                    self.error+="Error en el Script"


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
            while(self.cerrar.is_set()):
                pass
            while (not self.qEnt.empty()):
                #self.checkQueue()
                self.qEnt.get()
            while (not self.qSal.empty()):
                self.qSal.get()
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
    #Window.maximize()
    Innterfaz().run()

