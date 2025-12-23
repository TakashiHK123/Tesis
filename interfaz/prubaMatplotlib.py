import numpy as np
import matplotlib.pyplot as plt
# import pandas as pd
import os

from scipy.signal import find_peaks
import time
import threading
# plt.rc('font', size=12)          # controls default text sizes
# plt.rc('axes', titlesize=16)     # fontsize of the axes title
# plt.rc('axes', labelsize=16)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=14)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=13)    # fontsize of the tick labels

# plt.figure(1)
# b=plt.plot([69,42],[42,69])
# plt.figure(2)
# a=plt.plot([690,420,8],[420,690,0])

# print(plt.figure(2))
# # plt.clf()
# #plt.plot([1,2],[1,2])
# #plt.show()
# print(plt.gcf())
# a=plt.gcf()
# a.savefig("adhabhdha.png")
# # plt.show()


#df = pd.read_csv('entrada\entradaMuchos.csv', header=None)
#y = df.to_numpy()
n=1
for archivo in os.listdir("entradaSinMosquitos"):
    y=np.loadtxt("entradaSinMosquitos/"+str(archivo))
    #y=np.loadtxt("entrada/"+str(archivo))#'entrada\entradaMuchos.csv'
    x = np.arange(0, y.shape[0])#/2000
    #print("Shape of the NumPy array:", A.shape)
    #print("First 5 elements of the NumPy array:\n", A[:5])
    plt.figure(n)
    y=y-np.mean(y)
    fig, axs =plt.subplots(nrows=1, ncols=1)
    axs.plot(x, y)
    peaks, _ = find_peaks(y,threshold=0.0005,height=0.0005)#,prominence=(None, 5)
    axs.scatter(peaks,y[peaks],color="r")

    peaks_min, _ = find_peaks(-y,threshold=0.0005,height=0.0005)#,distance=2,width=1,threshold=0.0005,height=0.0005
    axs.scatter(peaks_min,y[peaks_min],color="g")
    par_ent=[]
    par_sal=[]
    sal=[]
    ent=[]
    #print(peaks,peaks_min)
    for i in peaks:
        for j in peaks_min:
            if 0<j-i<11:
                par_ent.append([i,j])
                ent.append((i+j)//2)
            elif 0<i-j<11:
                par_sal.append([i,j])
                sal.append((i+j)//2)
    if len(ent)>0:
        axs.scatter(ent,y[ent],color="y",marker=">")
    if len(sal)>0:
        axs.scatter(sal,y[sal],color="r",marker="<")
    
    # h=1

    # dydx=(y[2:]-y[:-2])/(2*h)
    # # plt.figure(2)
    # #axs[0].plot(x[2:], dydx)

    # dy2dx=(y[4:]-2*y[2:-2]+y[:-4])/(4*h*h)
    # #axs[0].plot(x[4:], dy2dx)

    n+=1
    plt.title(str(archivo)+"  "+str(len(par_ent))+"  "+str(len(par_sal)))


    #a=np.array([0,0,0,0,0.15,0.5,1,0,-0.75,-1,-0.2,-0.05,0,0,0,0])*0.01
    # a=np.array([0.15,0.5,1,0,-1,-0.5,-0.15])*0.01
    # a=a-np.mean(a)
    # relacion=[]
    # nn=a.shape[0]
    # k=dydx.shape[0]- nn
    # #k=y.shape[0]- nn
    # for i in range(k):
    #     aux=dydx[i:i+nn]-np.mean(dydx[i:i+nn])-a 
    #     #aux=y[i:i+nn]-np.mean(y[i:i+nn])-a
    #     relacion.append(np.dot(aux,aux))
    #     #relacion.append(np.corrcoef(a,dydx[i:i+nn])[0,1])
    # relacion=np.sqrt(np.array(relacion))
    # relacion-=np.mean(relacion)
    # relacion=-relacion
    # #relacion=1-(np.array(relacion))*6/(nn*(nn**2-1))
    # peaks, _ = find_peaks(relacion,height=0.0025,distance=3)
    # axs[1].plot(relacion)
    # axs[1].plot([0,relacion.shape[0]-1],[0.0075,0.0075])
    # axs[1].scatter(peaks,relacion[peaks],color="r")

#y=np.loadtxt("entrada\entradaMuchos.csv")
#y=np.loadtxt("entrada\salidaMuchos.csv")
#y=np.loadtxt("entrada/2mosquitosEntrada.csv")
y=np.loadtxt("entrada/3mosquitosEntrada.csv")


tiempo=time.time()
# global c
# global sali
#global cont
global k
#global npmax
global npmin
c=[[],[]]
sali=[]
k=0
nnn=15
a=y.shape[0]-nnn
npmax=0
npmin=0


def funcion(datos,x):
    global npmin
    datos=datos-np.mean(datos)
    peaks, _ = find_peaks(datos,threshold=0.0005,height=0.0005)#,threshold=0.0005,height=0.0005
    #npmax+=1
    if len(peaks)>0:
        peaks_min, _ = find_peaks(-datos,threshold=0.0005,height=0.0005)#,threshold=0.0005,distance=2,width=0.6
        npmin+=1
    else:
        return 0
    for i in peaks:
        # if k:
        #     k=0
        #     break
        for j in peaks_min:
            if 0<j-i<11:
                c[0].append(x+i)
                c[1].append(x+j)
                sali.append((i+j)//2+x)
                # k=nnn
                return 1
            elif j-i>10:
                break
    return 0

def funcion2(datos,x):
    global npmin
    m=np.mean(datos)
    #datos=datos-m
    if max(datos)>m+0.001 and min(datos)<m-0.001:
        i=np.argmax(datos)
        j=np.argmin(datos)
        if j>i:#0<j-i<11:
            c[0].append(x+i)
            c[1].append(x+j)
            sali.append((i+j)//2+x)
            return 1
        
    return 0

for x in range(a):
    if x%5==0:
        if k:
            k-=5
            continue
        datos=y[x:x+nnn]
        npmax+=1
        k=funcion2(datos,x)*nnn
        # t=threading.Thread(target=funcion,args=(datos,x))
        # t.start()
        #t.join()
#print(c)  
tiempo=time.time()-tiempo
print("tiempo: ",tiempo," s,  npmax: ",npmax," ,  npmin: ",npmin," , tiempo/peak: ", 1000000*(tiempo)/(npmin+npmax)," us")     
print(len(sali))
plt.figure(n+1)
plt.plot(y)
plt.scatter(sali,y[sali],color="m",marker=">")
plt.scatter(c[0],y[c[0]],color="r",marker="o")
plt.scatter(c[1],y[c[1]],color="g",marker="o")




plt.show()


