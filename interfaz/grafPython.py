import numpy as np
import matplotlib.pyplot as plt
import os
import time
import librosa
import librosa.display
from scipy.signal import butter,filtfilt,find_peaks

texto="mediciones/infrarrojo/2025-11-11 20-01-50.txt"
#texto="mediciones/infrarrojo/2025-09-16 00-15-05.txt"
#texto="mediciones/infrarrojo/2025-11-11 18-32-20.txt"
x=np.loadtxt(texto)
tiempo=x[0]
print(tiempo," s. Estimado de muestras no leidas: " ,(tiempo-10)*3750, ". en porcentaje: ",(tiempo-10)/(10+tiempo)*100 ,"%")
x=np.delete(x,0)

#24 bits

plt.figure(1)

#plt.scatter(range(len(x)),x,marker="o")
error=[]
for i in range(len(x)-4):
    if abs(x[i+1]-x[i+3])<0.002:
        if abs(x[i]-x[i+1])<0.002 and abs(x[i+3]-x[i+4])<0.002:

            if x[i+1]-x[i+2]>0.008:
                #if (x[i]-x[i+1])/abs(x[i]-x[i+2])>10:
                error.append(i+2)
                #x[i+2]=(x[i+1]+x[i+3])/2
print(error)
plt.scatter(error,x[error],marker="x",color="r")



plt.plot(x)

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

plt.figure(2)
    
librosa.display.specshow(spectrogram_db,sr=sr, hop_length=hop_length, x_axis='time', y_axis='linear')
plt.ylim([min_freq, max_freq])
plt.title('Espectrograma de señal infrarroja ')
plt.colorbar(format='%+2.0fdb')
plt.tight_layout()
    
#---------------------------------------------------------------------------
#solo hasta 16 bits
x=np.delete(np.loadtxt(texto),0)#,dtype="float32"
#x=np.round(x, decimals=4)
x=x*8388608/5.0
x=x.astype(np.int32)
x=np.bitwise_and(x,np.ones(x.shape[0],dtype=np.int32)*(0x807FFF00))# 0x807FFF00 16 bits, 0x807FFFFF 24bits, 0x807FF000 12 bits
x=x.astype(np.float64)
x=x/8388608*5.0
plt.figure(3)


error=[]
for i in range(len(x)-4):
    if abs(x[i+1]-x[i+3])<0.002:
        if abs(x[i]-x[i+1])<0.002 and abs(x[i+3]-x[i+4])<0.002:

            if x[i+1]-x[i+2]>0.008:
                #if (x[i]-x[i+1])/abs(x[i]-x[i+2])>10:
                error.append(i+2)
                x[i+2]=(x[i+1]+x[i+3])/2
print(error)
plt.scatter(error,x[error],marker="x",color="r")
plt.plot(x)


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

plt.figure(4)
    
librosa.display.specshow(spectrogram_db,sr=sr, hop_length=hop_length, x_axis='time', y_axis='linear')
plt.ylim([min_freq, max_freq])
plt.title('Espectrograma de señal infrarroja ')
plt.colorbar(format='%+2.0fdb')
plt.tight_layout()







# plt.figure(5)
# sr=1000
# #datos+=np.sin(np.linspace(0,4*sr*np.pi,sr*10))
# datos=np.sin(np.concatenate((np.concatenate((np.zeros(5*sr), np.linspace(0,np.pi,sr))),np.zeros(4*sr))))*5*np.sin(np.linspace(0,0.8*sr*np.pi/5,10*sr))
# datos+=np.sin(np.linspace(0,1/16*np.pi*sr,sr*10))*0.5 
# #datos+=np.random.normal(0, 1, sr*10)
# T=np.linspace(0,10,sr*10)
# plt.plot(T,datos)

# plt.figure(6)
# fft_data = np.fft.fft(datos)
# fft_freq = np.fft.fftfreq(len(datos),1/ sr)
# valid_freq_indices = np.where((fft_freq >= 0 ))[0] 
# magnitude_spectrum = np.abs(fft_data)
# plt.plot(fft_freq[valid_freq_indices], magnitude_spectrum[valid_freq_indices])
# plt.xlim([0, 40])
# plt.ylabel('Intensidad (V/Hz)')
# plt.xlabel('Frecuencia (Hz)')

# plt.figure(7)

# spectrogram = librosa.stft(datos)
# spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram))
# librosa.display.specshow(spectrogram_db,sr=sr, x_axis='time', y_axis='linear')
# plt.ylim([0, 40])
plt.show()