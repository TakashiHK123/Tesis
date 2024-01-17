import numpy as np
import matplotlib.pyplot as plt
import pywt
import sounddevice as sd

# Configuración de grabación
fs = 44100  # Frecuencia de muestreo
duration = 5  # Duración de la grabación en segundos

# Grabar audio desde el micrófono USB
print("Grabando...")
audio = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype=np.int16)
sd.wait()
#---Otro ejejmplo a probar
#import sounddevice as sd

# Mostrar información sobre los dispositivos de entrada disponibles
print(sd.query_devices())

# Seleccionar el micrófono por su identificador de dispositivo##Lo mas probable que se use esto
#mic_id = 0  # Ajusta el valor según la salida de sd.query_devices()
#audio = sd.rec(frames=44100, channels=1, samplerate=44100, dtype='int16', device=mic_id)
#sd.wait()
#---------------------------------------------------------------------------------------------

# Convertir a array unidimensional
audio = audio.flatten()

# Seleccionar una wavelet (por ejemplo, Daubechies 4)
wavelet = 'db4'

# Descomposición de la señal utilizando la Transformada Wavelet
coeffs = pywt.wavedec(audio, wavelet)

# Graficar los coeficientes de la descomposición
plt.figure(figsize=(12, 8))
for i in range(len(coeffs)):
    plt.subplot(len(coeffs), 1, i+1)
    plt.plot(coeffs[i])
    plt.title(f'Detalles de nivel {i+1}')

plt.tight_layout()
plt.show()

# Guardar la señal procesada en un archivo de audio WAV
wavfile.write('audio_procesado.wav', fs, audio)

# Calcular la frecuencia del zumbido del mosquito (ajusta según tus necesidades)
frecuencia_zumbido = calcular_frecuencia_zumbido(coeffs, fs)

print(f"Frecuencia del zumbido del mosquito: {frecuencia_zumbido} Hz")
