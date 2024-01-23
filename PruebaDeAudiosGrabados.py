import os
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

# Ruta del archivo WAV dentro de la carpeta "audio"
archivo_audio = 'audio/Mosquito:2fecha:2024-01-23_16-40-04.wav'  # Ajusta el nombre del archivo según tus necesidades

# Suponiendo que ya tienes la frecuencia de referencia
frecuencia_maxima_esperada = 630  # Por ejemplo, 440 Hz para el tono de La
frecuencia_minima_esperada = 500  # Ajusta según tus necesidades

# Cargar el archivo WAV
fs, audio_grabado = wavfile.read(archivo_audio)

# Asegurarse de que los datos son de tipo int16
datos = audio_grabado.astype(np.int16)

audio_grabado = audio_grabado / np.max(np.abs(audio_grabado))
ventana = np.hanning(len(audio_grabado))
audio_grabado_ventaneado= audio_grabado*ventana
# Aplicar la Transformada de Fourier (FFT)
fft_resultado = np.fft.fft(audio_grabado_ventaneado)
frecuencias = np.fft.fftfreq(len(fft_resultado), 1 / fs)

# Encontrar la frecuencia dominante
indice_frecuencia_dominante = np.argmax(np.abs(fft_resultado))
frecuencia_dominante = frecuencias[indice_frecuencia_dominante]
# Visualizar el espectro de frecuencia
plt.plot(frecuencias, np.abs(fft_resultado))
plt.xlabel('Frecuencia (Hz)')
plt.ylabel('Amplitud')
plt.title('Espectro de frecuencia')
plt.show()
# Verificar si la frecuencia corresponde a la esperada
if frecuencia_dominante<=frecuencia_maxima_esperada and frecuencia_dominante>=frecuencia_minima_esperada:
    print(f"El audio en {archivo_audio} corresponde a la frecuencia esperada.")
else:
    print(f"El audio en {archivo_audio} no corresponde a la frecuencia esperada.")
