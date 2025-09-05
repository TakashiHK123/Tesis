from progPrueba import ejemplo as pP
#from ProgFinal import mainPPI as pP

if __name__ == '__main__': #tuve que hacer esto para que no se abra una segunda ventana de kivy al ejecutar el Process,
                           # segun lo que lei en linux no deberia ser necesario, solo en windows

    from kivy.app import App
    from kivy.uix.widget import Widget
    # from kivy.uix.button import Button
    from kivy.properties import StringProperty,NumericProperty,BooleanProperty,ObjectProperty,ListProperty
    #from kivy.uix.gridlayout import GridLayout
    #from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.boxlayout import BoxLayout
    from random import randint
    from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
    import matplotlib.pyplot as plt
    from kivy.uix.screenmanager import ScreenManager, Screen 
    from kivy.lang import Builder
    from kivy.clock import Clock
    from multiprocessing import Process, Queue, Event, Manager
    #from kivy.config import Config
    from kivy.core.window import Window
    import cv2
    from kivy.graphics.texture import Texture
    import numpy as np
    import librosa
    import librosa.display
    import time
    from scipy.signal import butter,filtfilt
    import os
    import json
    import threading,queue
    from datetime import datetime
    import wave

    if not os.path.exists("mediciones"):
        os.makedirs("mediciones")
    
    if not os.path.exists("mediciones/camara"):
        os.makedirs("mediciones/camara")
    
    if not os.path.exists("mediciones/infrarrojo"):
        os.makedirs("mediciones/infrarrojo")

    if not os.path.exists("mediciones/microfono"):
        os.makedirs("mediciones/microfono")


    ConfigFile="interfaz/configfile.json"
    if os.path.exists(ConfigFile):
        with open(ConfigFile, 'r') as file:
            # Load the JSON data from the file
            json_data = json.load(file)
    else:
        json_data = {
            "Posiciones":[0,1,2,10,3,3,3],
            "Turbina":[1465,1400,1600],
            "MosquitosAIngresar":1,
            "Turbina+Camara":False,
            "tipoDemedicion":0
        }
        with open(ConfigFile, 'w') as file:
            # Dump the Python object as JSON to the file
            json.dump(json_data, file, indent=4) # indent for pretty-printing


    manager=Manager()


    # bufferless VideoCapture
    class VideoCapture:

        def __init__(self, name):
            self.cap = cv2.VideoCapture(name)
            self.q = queue.Queue()
            self.t = threading.Thread(target=self._reader)
            self.t.daemon = True
            self.t.start()

        # read frames as soon as they are available, keeping only most recent one
        def _reader(self):
            try:
                while True:
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                    if not self.q.empty():
                        try:
                            self.q.get_nowait()   # discard previous (unprocessed) frame
                        except queue.Empty:
                            pass
                    self.q.put(frame)
            except:
                pass#print("popo")

        def read(self):
            if self.q.empty():
                return 0,0
            return 1,self.q.get()
        
        def release(self):
            try:
                self.cap.release()
                self.t.join()
            except:
                print("cagada")
        
        def isOpened(self):
            return self.cap.isOpened()

  
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
    plt.rc('font', size=12)          # controls default text sizes
    plt.rc('axes', titlesize=16)     # fontsize of the axes title
    plt.rc('axes', labelsize=16)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=14)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=13)    # fontsize of the tick labels

    class FirstWindow(Screen):
        pass

    class SecondWindow(Screen):
        pass

    class ThirdWindow(Screen):
        pass

    class WindowManager(ScreenManager):
        pass

    class Innterfaz(App):
        pCorriendo=BooleanProperty(False)
        botonScript=StringProperty("Iniciar Programa")
        ultimaMedicion=StringProperty("nada")
        ultimoGrafico=StringProperty("nada")
        contM=NumericProperty(0)
        contH=NumericProperty(0)
        contMix=NumericProperty(0)
        fpsvideo=NumericProperty(20.0)
        contNada=NumericProperty(0)
        guardado=BooleanProperty(False)
        pasoEnCicloAutomatico=NumericProperty(0)
        estado = StringProperty('Trampa\nApagada')
        modoManual =BooleanProperty(True)
        frecD=NumericProperty(0)
        error=StringProperty("")
        ocupado=BooleanProperty(False)
        video=BooleanProperty(False)
        videoyadc=BooleanProperty(False)
        foto=BooleanProperty(False)
        fotoCorrecta=BooleanProperty(False)
        grabando=BooleanProperty(False)
        tipoDemedicion=NumericProperty(json_data["tipoDemedicion"])
        texture=ObjectProperty(image_texture)
        plotADC=ObjectProperty()
        rangoH =BooleanProperty(0)
        rangoM =BooleanProperty(0)
        Posiciones=ListProperty(json_data["Posiciones"])
        turbina=manager.list()
        for i in json_data["Turbina"]: #[1465,1400,1600]
            turbina.append(i)
        variablesCompartidas=manager.dict()
        variablesCompartidas["MosquitosEnLaTrampa"]=0
        variablesCompartidas["MosquitosAIngresar"]=json_data["MosquitosAIngresar"]
        variablesCompartidas["Turbina+Camara"]=json_data["Turbina+Camara"]
        variablesCompartidas["Salida"]=0
        variablesCompartidas["Audio"]=None
        variablesCompartidas["AudioGraf"]=None
        variablesCompartidas["ADC"]=None
        variablesCompartidas["graficoADC"]=None
        variablesCompartidas["graficoAudio"]=None
        variablesCompartidas["rangoH"]=None
        variablesCompartidas["rangoM"]=None
 
        def graficar(self,A):
            self.ultimoGrafico=A
            self.graficarKivy(A)
            self.rangoH=self.variablesCompartidas["rangoH"]
            self.rangoM=self.variablesCompartidas["rangoM"]
            

        def graficarKivy(self,A,dt=0):
            self.borrarGrafico() # si no pongo esto se acumlan graficos encimados y se vuelve lento el programa
            if A=="ADC":
                grafico=self.variablesCompartidas["graficoADC"]
            elif A=="Audio":
                grafico=self.variablesCompartidas["graficoAudio"]
            self.box = BoxLayout(size_hint=(1, 1))
            self.box.add_widget(FigureCanvasKivyAgg(grafico))
            # self.box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
            self.root.get_screen('first').ids.grafico.add_widget(self.box)

            
        def guardarMedicion(self):
            fecha=self.fecha()
            if self.ultimaMedicion=="Audio" or self.ultimaMedicion=="Audio+Infrarrojo":
                wf = wave.open(f"mediciones/microfono/{fecha}.wav", 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 2 bytes para formato PCM_FORMAT_S16_LE
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.variablesCompartidas["Audio"]))
                wf.close()
                self.variablesCompartidas["graficoAudio"].savefig(f"mediciones/microfono/{fecha}.png")
            if self.ultimaMedicion=="ADC" or self.ultimaMedicion=="Audio+Infrarrojo" or self.ultimaMedicion=="Infrarrojo+Video":
                with open(f"mediciones/infrarrojo/{fecha}.txt",'w') as file:
                    for i in self.variablesCompartidas["ADC"]:
                        file.write(str(i)+"\n")
                self.variablesCompartidas["graficoADC"].savefig(f"mediciones/infrarrojo/{fecha}.png")
            if self.ultimaMedicion=="Infrarrojo+Video":
                try:
                    os.rename(f"mediciones/camara/temporal.mp4", f"mediciones/camara/{fecha}.mp4")
                except:
                    pass
            self.guardado=True

        
        def sgteLugar(self,x,op=1):
            if op:
                return [(x+1)%7,(-1),13][(x==6)+(x==-1)*2]
            else:
                return (x+1)%7+(x==6)*(-1)

        def borrarGrafico(self):
            try:
                self.guardado=False
                self.root.get_screen('first').ids.grafico.remove_widget(self.box)
            except:
                pass #xd
        
        def mensajeError(self):
            a=self.error.split("\n")
            self.error="\n".join(a[-4:])

        def checkQueue(self,dt=0):
            if not self.qEnt.empty():
                A=self.qEnt.get()
                if A=="Audio" or A=="ADC" or A=="Audio+Infrarrojo":
                    self.ultimaMedicion=A
                    self.graficar(A)
                elif A=="Infrarrojo+Video":
                    if self.grabando:
                        self.pararVideo()
                        self.ultimaMedicion=A
                        self.graficar("ADC")
                    else:
                        self.grabarVideo()
                    
                elif A=="NuevoEstado":
                    x=self.qEnt.get()
                    self.estado=x
                    
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
                            
                elif A=="FinAccion":
                    self.ocupado=False

                elif A=="video" or A=="videoyadc":
                    self.cap = VideoCapture(0)#VideoCapture('http://192.168.100.26:8080/video')
                    if not self.cap.isOpened():
                        self.error+="Error con la camara\n"
                        self.mensajeError()
                        print("Error: No se puede acceder a la cámara. ¿Está conectada correctamente?")
                        self.qSal.put("Error")
                        self.ocupado=False
                    else:
                        if self.modoManual:
                            self.video=True
                            if A=="videoyadc":
                                self.videoyadc=True
                            Clock.schedule_interval(self.videoCapture, 1.0/self.fpsvideo)
                            self.qSal.put("camaraPrendida")
                            
                        else:
                            time.sleep(0.5)
                            self.videoCapture()
                            self.guardarImagen()
                            self.qSal.put("pararVideo")
                            
                
                elif A=="pararVideo":
                    self.pararVideo()

                elif A=="cierrePorError":
                    self.pararPrograma()
                    self.error+="Error en el Programa\n"
                    self.mensajeError()


        def pararVideo(self):
            Clock.unschedule(self.videoCapture)
            self.cap.release()
            #cv2.destroyAllWindows()
            self.ocupado=False
            self.video=False
            self.foto=False
            self.videoyadc=False
            if self.grabando:
                self.pararGrabacion()

        def guardarImagen(self):
            if self.fotoCorrecta:
                cv2.imwrite(f"mediciones/camara/{self.fecha()}.jpg",self.frame)
            else:
                self.error+="Error al guardar la foto\n"
                self.mensajeError()
            self.foto=False
            
        
        def grabarVideo(self):
            #self.grabacion = cv2.VideoWriter('videoSalida.avi',cv2.VideoWriter_fourcc(*'XVID'),20.0,(640,480))
            height, width, channels = self.frame.shape
            if self.videoyadc==True:
                self.direccionVideo=f"mediciones/camara/temporal.mp4"
            else:
                self.direccionVideo=f"mediciones/camara/{self.fecha()}.mp4"

            self.grabacion = cv2.VideoWriter(self.direccionVideo, cv2.VideoWriter_fourcc(*'mp4v'), self.fpsvideo, (width,height))
            self.grabando = True

        def pararGrabacion(self):
            try:
                self.grabacion.release()
            except:
                pass

            self.grabando = False

        def videoCapture(self,dt=0):
            if not self.foto:
                self.fotoCorrecta, self.frame = self.cap.read()
                if not self.fotoCorrecta:
                    #print("Error al leer el fotograma")
                    return
                buf1 = cv2.flip(self.frame, 0)
                buf = buf1.tobytes()#.tostring()
                image_texture = Texture.create(
                    size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture=image_texture
                if self.grabando==True:
                    self.grabacion.write(self.frame)

        def cicloAutomatico(self,dt=0):
            if not self.ocupado and self.pCorriendo:
                if self.pasoEnCicloAutomatico==0:
                    self.qSal.put("Posicion Inicial")
                elif self.pasoEnCicloAutomatico==1:
                    self.qSal.put("ADC")
                elif self.pasoEnCicloAutomatico==2:
                    self.guardarMedicion()
                    self.qSal.put("video")
                elif self.pasoEnCicloAutomatico==3:
                    self.qSal.put("Soltar Mosquito") 
                self.pasoEnCicloAutomatico=(self.pasoEnCicloAutomatico+1)%4
                self.ocupado=True


        def CambiarModo(self):
            self.modoManual=not self.modoManual
            if self.modoManual:
                Clock.unschedule(self.cicloAutomatico)
            else:
                Clock.schedule_interval(self.cicloAutomatico, 1.0/2)
                self.pasoEnCicloAutomatico=0


        def iniciarPrograma(self):
            if self.pCorriendo:
                self.pararPrograma()
            else:
                self.pCorriendo=1
                self.ocupado=False
                self.qEnt=Queue() 
                self.qSal=Queue() 
                self.cerrar=Event()
                self.p=Process(target=pP,args=(self.qEnt,self.qSal,self.cerrar,self.turbina,self.variablesCompartidas))
                self.p.start()

                self.botonScript="Cerrar Programa"
                if not self.modoManual:
                    Clock.schedule_interval(self.cicloAutomatico, 1.0/2)
                    self.pasoEnCicloAutomatico=0
                Clock.schedule_interval(self.checkQueue, 1.0/5)

        def pararPrograma(self):
            try:
                self.pararVideo()
            except:
                pass
            Clock.unschedule(self.checkQueue)
            Clock.unschedule(self.cicloAutomatico)
            
            # self.p.terminate()
            self.cerrar.set()
            tiempo=time.time()
            aux=0
            while(self.cerrar.is_set()):
                if time.time()-tiempo >5:
                    aux=1
                    break
            while (not self.qEnt.empty()):
                self.qEnt.get()
            while (not self.qSal.empty()):
                self.qSal.get()
            if aux:
                self.p.kill()
                self.qEnt.close()
                self.qSal.close()
                self.error+="Cierre Forzdo (+5s)\n"
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
            self.ocupado=False
            self.estado='Trampa\nApagada'
            self.botonScript="Iniciar Programa"

        def save_json(self):
            json_data["Posiciones"]=self.Posiciones
            json_data["Turbina"]=[self.turbina[0],self.turbina[1],self.turbina[2]]
            json_data["MosquitosAIngresar"]=self.variablesCompartidas["MosquitosAIngresar"]
            json_data["Turbina+Camara"]=self.variablesCompartidas["Turbina+Camara"]
            json_data["tipoDemedicion"]=self.tipoDemedicion
            with open(ConfigFile, 'w') as file:
                json.dump(json_data, file, indent=4) 

        def fecha(self):
            current_datetime = datetime.now()
            return current_datetime.strftime("%Y-%m-%d %H-%M-%S")


        def updateWid(self,dt=0):
            self.root.get_screen('first').ids.MosquitosEnLaTrampa.text="Mosquitos en la trampa:\n\n"+str(self.variablesCompartidas["MosquitosEnLaTrampa"])


        def on_start(self):
            Clock.schedule_interval(self.updateWid, 1.0)
            pass

        def on_stop(self):
            Clock.unschedule(self.updateWid)
            if self.pCorriendo:
                self.pararPrograma() 
            self.save_json()

        def build(self):
            return Builder.load_file('interfaz.kv')


if __name__ == '__main__':
    
    # Config.set('graphics', 'resizable', '0')
    # Config.set('graphics', 'width', '480')
    # Config.set('graphics', 'height', '320')
    Window.size = (800, 600)
    #Window.fullscreen = True
    #Window.maximize()
    #os.system("xrandr --output HDMI-1 --mode 720x480")
    Innterfaz().run()

