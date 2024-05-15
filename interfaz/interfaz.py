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
                if A=="Graficar":
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
                    self.cap = cv2.VideoCapture(2)
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
                    Clock.unschedule(self.videoCapture)
                    self.cap.release()
                    cv2.destroyAllWindows()
                    self.ocupado=False
                    self.video=False


        def videoCapture(self,dt=0):
            ret, frame = self.cap.read()
            if not ret:
                print("Error al leer el fotograma")
                return
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tobytes()#.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture=image_texture


        def iniciarPrograma(self):
            if self.pCorriendo:
                self.pararPrograma()
                self.botonScript="Iniciar Script"
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
                Clock.schedule_interval(self.checkQueue, 1)

        def pararPrograma(self):
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
                self.p.terminate()
                print("error al cerrar")
            self.pCorriendo=0
            self.estado='Trampa\nApagada'

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

