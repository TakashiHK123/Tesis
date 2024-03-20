import random
import time
import numpy as np
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


def ejemplo(queue=FakeClass(),parada=FakeClass()):
    # signal.signal(signal.SIGTERM, handle_exit)  #probar en linux, en windows no funciona
    # signal.signal(signal.SIGINT, handle_exit)
    try:
        print("holaa")
        y=np.zeros(1024)
        x=np.zeros(1024)
        while(True):
            print("looop")
            if parada.is_set():
                raise KeyboardInterrupt('kk')
            time.sleep(2)
            for i in range(1024):
                y[i]=random.random()
                x[i]=i
            queue.put(y)
            queue.put(x)
    except KeyboardInterrupt as e:
        print('exit handled')
        #queue.close()
        print(e)
        #time.sleep(5)
        parada.clear()
        return None
        



if __name__ == '__main__':
    print("Main")
    ejemplo()