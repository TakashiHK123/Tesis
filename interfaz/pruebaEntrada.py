import numpy as np
import matplotlib.pyplot as plt
import os
import time


n=0
for archivo in os.listdir("entrada"):
    #y=np.loadtxt("entradaSinMosquitos/"+str(archivo))
    y=np.loadtxt("entrada/"+str(archivo))#'entrada\entradaMuchos.csv'
    # y+=1
    # y=y*8388608.0/5.0
    # y=y.astype(np.int32)
    # y=np.bitwise_and(y,np.ones(y.shape[0],dtype=np.int32)*(0x807FFF00))# 0x807FFF00 16 bits, 0x807FFFFF 24bits, 0x807FF000 12 bits
    # y=y.astype(np.float64)
    # y=y/8388608.0*5.0
    # y-=1

    #diezmado
    #y=y[::2]

    global cont
    cont=0
    c=[[],[]]
    entradasM=[]
    salidasM=[]
    threshold=0.001
    def funcion2(datos,x):
        m=np.mean(datos)
        global cont
        if max(datos)>m+0.001 and min(datos)<m-0.0003:
            i=np.argmax(datos)
            j=np.argmin(datos)
            cont+=1
            if j>i:#0<j-i<11:
                if max(datos)>np.mean(datos[:i+1])+0.0005 and min(datos)<np.mean(datos[j:])-0.00015:
                    c[0].append(x+i)
                    c[1].append(x+j)
                    entradasM.append((i+j)//2+x)
                    return 1
            else:
                if max(datos)>np.mean(datos[i:])+0.0005 and min(datos)<np.mean(datos[:j+1])-0.00015:
                    c[0].append(x+i)
                    c[1].append(x+j)
                    salidasM.append((i+j)//2+x)
        return 0
    
    nnn=15
    a=y.shape[0]-nnn
    k=0
    for x in range(a):
        if x%5==0 and x>15:
            if k:
                k-=5
                continue
            datos=y[x-15:x+1]
            k=funcion2(datos,x-15)*nnn
    
    n+=1
    plt.figure(n)
    #print(len(entradasM))
    plt.plot(y)
    plt.scatter(entradasM,y[entradasM],color="m",marker=">")
    plt.scatter(salidasM,y[salidasM],color="y",marker="<")
    plt.scatter(c[0],y[c[0]],color="r",marker="o")
    plt.scatter(c[1],y[c[1]],color="g",marker="o")
    plt.title(str(archivo)+"  "+str(len(entradasM))+"  "+str(len(salidasM))+"  "+str(cont))
    plt.xlabel("Muestras")
    plt.ylabel("Volts")

plt.show()