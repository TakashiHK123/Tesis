import random
import time
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2 
import sys


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

def ejemplo(queueSal=FakeClass(),queueEnt=FakeClass(),cierre=FakeClass()):
    # signal.signal(signal.SIGTERM, handle_exit)  #probar en linux, en windows no funciona
    # signal.signal(signal.SIGINT, handle_exit)
    try:
        l=[]
        T=[]
        # with open("/content/drive/MyDrive/p4/deteccionDeFrecTrampa/sinnada.txt","r") as a:
        with open("interfaz/medSoloHembras2.txt","r") as a:
        # with open("/content/drive/MyDrive/p4/deteccionDeFrecTrampa/medicionSoloMachos1.txt","r") as a:
            for line in a:
                try:
                    val , t=line.split(" ")
                    t=int(t)/1000000.0
                    #if True:#
                    if  t>=(0) and t<=(10):
                        val =float(val)
                        l.append(val)
                        T.append(t)
                except:
                    pass
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
        queueSal.put("NuevoEstado")
        queueSal.put("Iniciando")
        queueSal.put("Imagen")
        #queueSal.put("datos\mosquitos1_2024-03-05_01-26-23\imagen.jpg")
        queueSal.put(img)
        queueSal.put('ADC')
        queueSal.put(l)
        while(True):   
            # queueSal.put("Imagen")
            # queueSal.put(img)
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
                        if queueEnt.get()=="pararVideo":
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
            queueSal.put("Imagen")
            queueSal.put(img)
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