# import kivy
import progPrueba as pP
if __name__ == '__main__': #tuve que hacer esto para que no se abra una segunda ventana de kivy al ejecutar el Process,
                           # segun lo que lei en linux no deberia ser necesario, solo en windows

    from kivy.app import App
    from kivy.uix.widget import Widget
    # from kivy.uix.button import Button
    from kivy.properties import StringProperty,NumericProperty,BooleanProperty#,ObjectProperty
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
    

    

    plt.style.use("dark_background")


    class FirstWindow(Screen):
        pass

    class SecondWindow(Screen):
        pass

    class WindowManager(ScreenManager):
        pass

    class TercerWidget(Widget):
        pass

    class Innterfaz(App):
        pCorriendo=BooleanProperty(False)
        botonScript=StringProperty("Iniciar Script")
        imagen=StringProperty("tinky.jpeg")
        contM=NumericProperty(0)
        contH=NumericProperty(0)
        estado = StringProperty('Detectando\nMosquitos')
        modoManual =BooleanProperty(False)
        
        def funcPrueba(self):
            if self.estado != 'Detectando\nMosquitos':
                self.estado = 'Detectando\nMosquitos'
            else :
                self.estado = 'Mosquito\nDetectado'
                if randint(0,1):
                    self.contH +=1
                else :
                    self.contM +=1


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

        def checkQueue(self,dt=0):
            if not self.qEnt.empty():
                A=self.qEnt.get()
                if A=="Graficar":
                    y=self.qEnt.get()
                    x=self.qEnt.get()
                    plt.clf()
                    plt.plot(x,y)
                    plt.xlabel("Frecuencias (Hz)")
                    plt.ylabel("FFT")
                    self.graficar()
                elif A=="NuevoEstado":
                    x=self.qEnt.get()
                    self.estado=x
                elif A=="Imagen":
                    x=self.qEnt.get()
                    self.imagen=x


        def iniciarPrograma(self):
            if self.pCorriendo:
                self.pararPrograma()
                self.botonScript="Iniciar Script"
            else:
                self.pCorriendo=1
                self.qEnt=Queue() 
                self.qSal=Queue() 
                self.cerrar=Event()
                self.p=Process(target=pP.ejemplo,args=(self.qEnt,self.qSal,self.cerrar))
                self.p.start()
                self.botonScript="Cerrar Script"
                Clock.schedule_interval(self.checkQueue, 1)

        def pararPrograma(self):
            Clock.unschedule(self.checkQueue)
            # self.p.terminate()
            self.cerrar.set()
            while(self.cerrar.is_set()):
                pass
            while (not self.qEnt.empty()):
                self.checkQueue()
            while (not self.qSal.empty()):
                self.qSal.get()
            self.qEnt.close()
            self.qSal.close()
            self.p.join()
            self.pCorriendo=0

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

