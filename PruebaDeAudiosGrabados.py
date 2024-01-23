import os
import numpy as np
from scipy.io import wavfile

# Ruta del archivo WAV dentro de la carpeta "audio"
archivo_audio = 'audio/Mosquito:2fecha:2024-01-23_16-40-04.wav'  # Ajusta el nombre del archivo según tus necesidades

# Suponiendo que ya tienes la frecuencia de referencia
frecuencia_maxima_esperada = 630  # Por ejemplo, 440 Hz para el tono de La
frecuencia_minima_esperada = 500  # Ajusta según tus necesidades

# Cargar el archivo WAV
fs, audio_grabado = wavfile.read(archivo_audio)

# Aplicar la Transformada de Fourier (FFT)
fft_resultado = np.fft.fft(audio_grabado)
frecuencias = np.fft.fftfreq(1024, 1 / fs)

# Encontrar la frecuencia dominante
indice_frecuencia_dominante = np.argmax(np.abs(fft_resultado))
frecuencia_dominante = frecuencias[indice_frecuencia_dominante]

# Verificar si la frecuencia corresponde a la esperada
if frecuencia_dominante<=frecuencia_maxima_esperada and frecuencia_dominante>=frecuencia_minima_esperada:
    print(f"El audio en {archivo_audio} corresponde a la frecuencia esperada.")
else:
    print(f"El audio en {archivo_audio} no corresponde a la frecuencia esperada.")
