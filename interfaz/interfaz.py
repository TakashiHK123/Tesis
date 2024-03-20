# import kivy
import progPrueba as pP
if __name__ == '__main__': #tuve que hacer esto para que no se abra una segunda ventana de kivy al ejecutar el Process,
                           # segun lo que lei en linux no deberia ser necesario, solo en windows

    from kivy.app import App
    from kivy.uix.widget import Widget
    # from kivy.uix.button import Button
    from kivy.properties import StringProperty,NumericProperty#,ObjectProperty
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
    
    
    # x = [1,2,3,4,5]
    # y = [5, 12, 6, 9, 15]

    # plt.plot(x,y)
    # plt.ylabel("This is MY Y Axis")
    # plt.xlabel("X Axis")


    class FirstWindow(Screen):
        pass


    class SecondWindow(Screen):
        pass

    class WindowManager(ScreenManager):
        pass

    class PrimerWidget(Widget):   
        pass
        # text=StringProperty('Iniciar Script')
        # def callback(self):
        #     if self.text != 'Iniciar Script':
        #         self.text = 'Iniciar Script'
        #     else :
        #         self.text = 'Parar Script'


    class SegundoWidget(Widget):
        MosMacho = StringProperty('Cant. de Mosquitos Macho: 0')
        MosHembra = StringProperty('Cant. de Mosquitos Hembra: 0')
        contM=NumericProperty(0)
        contH=NumericProperty(0)
        text = StringProperty('Detectando\nMosquitos')
        def callback(self):
            if self.text != 'Detectando\nMosquitos':
                self.text = 'Detectando\nMosquitos'
            else :
                self.text = 'Mosquito\nDetectado'
                if randint(0,1):
                    self.contH +=1
                else :
                    self.contM +=1
                self.MosHembra='Cant. de Mosquitos Hembra: '+str(self.contH)
                self.MosMacho='Cant. de Mosquitos Hembra: '+str(self.contM)

    class TercerWidget(Widget):
        pass
        # text = StringProperty('tinky.jpeg')
        # def callback(self):
        #     print("e")


    class Innterfaz(App):
        pCorriendo=NumericProperty(0)
        botonScript=StringProperty("Iniciar Script")
        imagen=StringProperty("tinky.jpeg")

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
            if not self.q1.empty():
                y=self.q1.get()
                x=self.q1.get()
                plt.clf()
                plt.plot(x,y)
                plt.xlabel("Frecuencias")
                plt.ylabel("FFT")
                self.graficar()


        def iniciarPrograma(self):
            if self.pCorriendo:
                self.pararPrograma()
                self.botonScript="Iniciar Script"
            else:
                self.pCorriendo=1
                self.q1=Queue() 
                self.parada=Event()
                self.p=Process(target=pP.ejemplo,args=(self.q1,self.parada))
                self.p.start()
                self.botonScript="Cerrar Script"
                Clock.schedule_interval(self.checkQueue, 1)

        def pararPrograma(self):
            Clock.unschedule(self.checkQueue)
            # self.p.terminate()
            self.parada.set()
            while(self.parada.is_set()):
                pass
            while (not self.q1.empty()):
                self.checkQueue()
            self.q1.close()
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
    Innterfaz().run()

