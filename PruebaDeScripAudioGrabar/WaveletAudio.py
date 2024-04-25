import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

# Parámetros de grabación
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 30

# Inicializar PyAudio
audio = pyaudio.PyAudio()

# Configurar la grabación
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    input_device_index=2,
                    frames_per_buffer=CHUNK)

print("Grabando...")

frames = []

# Grabar audio
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Grabación finalizada")

# Detener y cerrar el flujo de audio
stream.stop_stream()
stream.close()
audio.terminate()

# Convertir la secuencia de audio a un array de numpy
audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

# Graficar la señal de audio
plt.figure(figsize=(10, 6))
plt.plot(audio_data)
plt.title('Señal de audio')
plt.xlabel('Tiempo (muestras)')
plt.ylabel('Amplitud')
plt.grid(True)
plt.show()

# Calcular la transformada wavelet
cwtmatr = signal.cwt(audio_data, signal.ricker, np.arange(1, 50))
# Guardar el audio grabado en un archivo WAV
wf = wave.open("AudioFondoCasaSinNada.wav", 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# Calcular la frecuencia nominal del audio
freqs, psd = signal.welch(audio_data, fs=RATE)
peak_freq = freqs[np.argmax(psd)]
print("Frecuencia nominal del audio:", peak_freq, "Hz")


# Graficar la transformada wavelet
plt.figure(figsize=(10, 6))
plt.imshow(cwtmatr, extent=[0, len(audio_data), 1, 50], cmap='jet', aspect='auto', vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
plt.colorbar(label='Escala de amplitud')
plt.title('Transformada wavelet continua')
plt.xlabel('Tiempo (muestras)')
plt.ylabel('Escala')
plt.show()

