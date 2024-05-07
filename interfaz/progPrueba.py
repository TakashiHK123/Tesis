import random
import time
import numpy as np
import os
import matplotlib.pyplot as plt
#import signal

# def handle_exit(sig, frame):
#     raise(SystemExit)

print("programa")

aa="holaaaa"

def prueba1():
    print("puebaaa")

class FakeClass():
    def __init__(self) -> None:
        pass
    def put(self,a):
        pass
    def get(self,a):
        pass
    def is_set(self):
        pass
    def empty(self):
        pass


#plt.plot([1,1.2],[4,5])

def ejemplo(queueSal=FakeClass(),queueEnt=FakeClass(),cierre=FakeClass()):
    # signal.signal(signal.SIGTERM, handle_exit)  #probar en linux, en windows no funciona
    # signal.signal(signal.SIGINT, handle_exit)
    try:
        if not os.path.exists("carpeta_pruebas"):
            os.makedirs("carpeta_pruebas")
        archivo=os.path.join("carpeta_pruebas", 'myfile.jpg')
        plt.savefig(archivo)
        tiempo=time.time()
        print("holaa")
        y=np.zeros(1024)
        x=np.zeros(1024)
        queueSal.put("NuevoEstado")
        queueSal.put("Iniciando")
        queueSal.put("Imagen")
        queueSal.put("datos\mosquitos1_2024-03-05_01-26-23\imagen.jpg")

        while(True):   
            if not queueEnt.empty():
                accion=queueEnt.get()
                print(accion)
            if cierre.is_set():
                raise KeyboardInterrupt('kk')
            #time.sleep(2)
            if time.time()-tiempo >5:
                print("nuevo grafico")
                for i in range(1024):
                    y[i]=random.random()
                    x[i]=i
                queueSal.put("Graficar")
                queueSal.put(y)
                queueSal.put(x)
                queueSal.put([500,400])
                queueSal.put([40,80])
                #queueSal.put("carpeta_pruebas\grafico.png")
                queueSal.put(None)
                tiempo=time.time()

    except KeyboardInterrupt as e:
        print('exit handled')
        #queue.close()
        print(e)
        #time.sleep(5)
        cierre.clear()
        #return None
        



if __name__ == '__main__':
    print("Main")
    ejemplo()