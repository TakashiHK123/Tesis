import numpy as np
import matplotlib.pyplot as plt
import pywt
import sounddevice as sd
from scipy.io import wavfile
from scipy.signal import find_peaks


def calcular_frecuencia_zumbido(coeffs, fs):
    # Obtener los coeficientes de detalle de alta frecuencia (último nivel)
    coeficientes_det_alta = coeffs[-1]

    # Aplicar un filtro para reducir el ruido
    coeficientes_det_alta_filtrados = aplicar_filtro(coeficientes_det_alta)

    # Definir el rango de frecuencias de interés (200 Hz a 1000 Hz)
    frecuencia_min = 200
    frecuencia_max = 1000

    # Encontrar los picos dominantes en el rango de frecuencias de interés
    indice_pico, _ = find_peaks(np.abs(coeficientes_det_alta_filtrados), height=amplitud_minima,
                                distance=int(fs / frecuencia_min),
                                prominence=(None, amplitud_minima))

    if len(indice_pico) > 0:
        # Filtrar picos dentro del rango de frecuencias de interés
        picos_en_rango = [i for i in indice_pico if frecuencia_min <= i * (fs / len(coeficientes_det_alta_filtrados)) <= frecuencia_max]

        if picos_en_rango:
            # Tomar el pico más prominente dentro del rango
            indice_pico_final = picos_en_rango[0]
            frecuencia_zumbido = indice_pico_final * (fs / len(coeficientes_det_alta_filtrados))
            return frecuencia_zumbido

    return None

def aplicar_filtro(signal):
    # Aquí puedes implementar algún tipo de filtro para reducir el ruido
    # Puedes explorar filtros específicos como un filtro de media móvil o un filtro pasa bajos
    return signal

# Configuración del filtro (ajusta según sea necesario)
amplitud_minima = 0.5
# Configuración de grabación
fs = 44100  # Frecuencia de muestreo
duration = 5  # Duración de la grabación en segundos

# Grabar audio desde el micrófono USB
print("Grabando...")
#audio = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype=np.int16)
mic_id = 2  # Ajusta el valor según la salida de sd.query_devices()
audio = sd.rec(frames=44100, channels=1, samplerate=44100, dtype='int16', device=mic_id)
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
