import numpy as np
import matplotlib.pyplot as plt
import os
import time
import librosa
import librosa.display
from scipy.signal import butter,filtfilt,find_peaks


n=0
for archivo in os.listdir("mediciones/infrarrojo"):
#for archivo in os.listdir("mediciones2"):
    if archivo.endswith(".txt"):
        # x=np.delete(np.loadtxt("mediciones/infrarrojo/"+str(archivo)),0)
        x=np.loadtxt("mediciones/infrarrojo/"+str(archivo))
        tiempo=x[0]
        #print(tiempo," s. Estimado de muestras no leidas: " ,(tiempo-10)*3750, ". en porcentaje: ",(tiempo-10)/(10+tiempo)*100 ,"%")
        x=np.delete(x,0)
        #x=np.delete(np.loadtxt("mediciones2/"+str(archivo)),0)
    else:
        continue
    
    #para quitar las zonas de mediciones desincronizdas
    ind=np.where(x<0)
    if len(ind[0]):
        aux=list(ind[0])
        for e in ind[0]:
            for j in range(e-10,e+10,1):
                if j>0 and j<len(x)-1:
                    aux+=[j]

        #datos[ind[0][0]-10:ind[0][-1]+10]=datos[ind[0][0]-10]
        if ind[0][0]-10>0:
            x[aux]=x[ind[0][0]-10]
        else:
            x[aux]=x[0]

    #para quitar las picos invertidos de 1 medicion
    for i in range(len(x)-4):
        if abs(x[i+1]-x[i+3])<0.002:
            if abs(x[i]-x[i+1])<0.002 and abs(x[i+3]-x[i+4])<0.002:
                if x[i+1]-x[i+2]>0.008:
                    x[i+2]=(x[i+1]+x[i+3])/2

    #----------------------------------
    fc_low = 250   # Lower cutoff frequency in Hz
    fc_high = 1200 # Upper cutoff frequency in Hz
    sr=3750


    nyquist = 0.5 * sr
    low = fc_low / nyquist
    high = fc_high / nyquist
    b, a = butter(6, [low, high], btype='band')
    x = filtfilt(b, a, x)

    n_fft=512

    hop_length = n_fft // 4
    min_freq=300
    max_freq=1200
    spectrogram = librosa.stft(x, n_fft=n_fft, hop_length=hop_length,center=False)
    spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=spectrogram.shape[0] * 2 - 1)
    
    #----------------------------------
    rangoH=0
    rangoM=0
    rangoH2=0
    rangoM2=0
    Hmin=400
    Hmax=600
    Mmin=680
    Mmax=900
    #--------------------------
    freqMachos=np.where((freqs >=Mmin) & (freqs <= Mmax))[0]
    freqHembras=np.where((freqs >=Hmin) & (freqs <=Hmax))[0]
    for i in spectrogram_db[freqMachos, :]:
        if i.max()>=-15:
            rangoM=1
            break
    for i in spectrogram_db[freqHembras, :]:
        if i.max()>=-13:
            rangoH=1
            break
    #----------------------------------
    hemb=[]
    mach=[]
    for v in range(spectrogram_db.shape[1]):

        specAux=spectrogram_db[:,v].copy()

        #para quitar 2do armonico de las hembras
        # auxi=np.where(specAux[np.where((freqs <= 650))[0]]>-35)[0]
        # for i in auxi:
        #     specAux[i*2]-=(specAux[i]+36)
        #     specAux[i*2+1]-=(specAux[i]+specAux[i+1])/2+36
        #--------------------------------------------------------
        

        #opcion 1:
        peaks, _ = find_peaks(specAux, distance=20,height=-25)#,threshold=2,width=10,threshold=1.5, prominence=0.2
        
        #opcion 2:
        #--------------------------------------------------------
        # window_size=10
        # specAux=spectrogram_db[:,v].copy()
  
        # for i in range(window_size-1):
        #     #specAux=np.append(specAux,specAux[-1])
        #     specAux=np.insert(specAux,0,specAux[0])
        # # Using convolution for a simple moving average
        # weights = np.ones(window_size) / window_size
        # specAux = np.convolve(specAux, weights, mode='valid') 

        # peaks, _ = find_peaks(specAux,height=-40, distance=20)#, distance=20, prominence=0.2), distance=100,threshold=1.5
        # peaks-=(window_size-1)//2
        #--------------------------------------------------------

        #opcion 0:
        if specAux[freqMachos].max()>-30:
            rangoM2+=1
            # mach.append([freqs[freqMachos[0]-1+specAux[freqMachos].argmax()],v])
        if specAux[freqHembras].max()>-30:
            rangoH2+=1
            # hemb.append([freqs[freqHembras[0]-1+specAux[freqHembras].argmax()],v])

        #--------------------------------------------------------
        machos=np.where((freqs[peaks] >=Mmin) & (freqs[peaks] <= Mmax))[0]
        if len(machos):
            mach.append([freqs[peaks[machos]],v])

        hembras=np.where((freqs[peaks] >=Hmin) & (freqs[peaks] <= Hmax))[0]
        if len(hembras):
            hemb.append([freqs[peaks[hembras]],v])

    #---------------------------
    # auxV=0
    # prevV=-100
    # for i in mach:
    #     if i[1]-prevV>5:
    #         auxV=0
    #     prevV=i[1]
    #     auxV+=len(i[0])
    #     if auxV>2:
    #         rangoM2=1
    #         break
    # auxV=0
    # prevV=-100
    # for i in hemb:
    #     if i[1]-prevV>5:
    #         auxV=0
    #     prevV=i[1]
    #     auxV+=len(i[0])
    #     if auxV>2:
    #         rangoH2=1
    #         break
    #----------------------------

    n+=1
    plt.figure(n)
    
    librosa.display.specshow(spectrogram_db,sr=sr, hop_length=hop_length, x_axis='time', y_axis='linear')
    plt.ylim([min_freq, max_freq])
    plt.title(str(archivo)+'.\nM1:'+str(rangoM)+" H1:"+str(rangoH)+' M2:'+str(rangoM2)+" H2:"+str(rangoH2)+"  %per: "+str((tiempo-10)/(10+tiempo)*100))
    plt.colorbar(format='%+2.0fdb')
    plt.tight_layout()
    plt.plot([0,9.8],[Hmin,Hmin],color="black")
    plt.plot([0,9.8],[Hmax,Hmax],color="black")
    plt.plot([0,9.8],[Mmin,Mmin],color="black")
    plt.plot([0,9.8],[Mmax,Mmax],color="black")
    for i in mach:
        a=np.ones(len(i[0]))*i[1]/spectrogram_db.shape[1]*9.8
        plt.scatter(a,i[0],color="green",marker="+")
    for i in hemb:
        a=np.ones(len(i[0]))*i[1]/spectrogram_db.shape[1]*9.8
        plt.scatter(a,i[0],color="cyan",marker="+")
    
plt.show()