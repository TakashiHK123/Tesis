import alsaaudio
import numpy as np
import matplotlib.pyplot as plt
import wave
import os
from datetime import datetime

def imprimir_clasificacion(clasificacion):
    if clasificacion:
        print("La clasificación más probable es:", clasificacion)
        return clasificacion
    else:
        print("No se pudo determinar la clasificación.")
        return None


def clasificar_frecuencia(high_magnitude_freq):
    try:
        high_magnitude_freq = [freq for freq in high_magnitude_freq if freq is not None]
        print("high_magnitude_freq:", high_magnitude_freq)

        # Verificar si la lista de frecuencias no está vacía
        if not high_magnitude_freq:
            print("Lista vacía.")
            return None

        # Frecuencias correspondientes a cada especie
        rangos = {
            "aedes_albopictus_macho": (450, 550),
            "aedes_albopictus_hembra": (730, 880),
            "culex_pipiens_macho": (360, 480),
            "culex_pipiens": (550, 730)
        }

        # Contador para contar la frecuencia de cada especie
        conteo_especies = Counter()

        # Iterar sobre las frecuencias y clasificarlas
        for freq in high_magnitude_freq:
            for especie, rango in rangos.items():
                if rango[0] <= freq <= rango[1]:
                    conteo_especies[especie] += 1

        # Obtener la especie con mayor frecuencia
        especie_mas_comun = conteo_especies.most_common(1)
        if especie_mas_comun:
            return especie_mas_comun[0][0]  # Devuelve la especie más común
        else:
            return None  # Devuelve None si no se detecta ninguna especie dentro de los rangos
    except Exception as e:
        print("Error:", e)
        return None  # Devuelve None si ocurre algún error durante el proceso de clasificación

class SoundDetector:
    def __init__(self):
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 512
        self.RECORD_SECONDS = 3

    def record_and_analyze(self, filename, save_plot_filename=None, input_device_index=None, repeat=False):
        while True:
            if input_device_index is None:
                input_device_index = self.get_default_input_device_index()

            stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, cardindex=input_device_index)
            stream.setchannels(1)
            stream.setrate(44100)
            stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            stream.setperiodsize(512)

            print("Grabando...")

            frames = []
            data = []

            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                length, audio_data = stream.read()
                frames.append(audio_data)
                data.extend(np.frombuffer(audio_data, dtype=np.int16))

            print("Fin de la grabación.")

            # Tu código de procesamiento aquí

            # Cerrar el dispositivo de audio
            stream.close()

            # Guardar los datos de audio en un archivo WAV
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(2)  # 2 bytes para formato PCM_FORMAT_S16_LE
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            # Procesamiento de los datos grabados
            data = np.array(data)

            fft_data = np.fft.fft(data)
            fft_freq = np.fft.fftfreq(len(data), 1 / self.RATE)
            magnitude_spectrum = np.abs(fft_data)

            # Identificar frecuencias que superan la magnitud de 0.2 dentro del rango de frecuencia especificado
            high_magnitude_indices = np.where((magnitude_spectrum > 0.5) & (fft_freq >= 200) & (fft_freq <= 1500))[0]
            high_magnitude_freq = fft_freq[high_magnitude_indices]


            # Visualización del espectro de magnitud
            plt.figure(figsize=(8, 4))
            plt.plot(fft_freq[:len(fft_freq) // 2], magnitude_spectrum[:len(fft_freq) // 2])
            plt.xlabel('Frecuencia (Hz)')
            plt.ylabel('Magnitud')
            plt.title('Espectro de Magnitud')
            plt.grid(True)

            # Resaltar las frecuencias que superan la magnitud de 0.2 dentro del rango de frecuencia especificado
            plt.plot(high_magnitude_freq, magnitude_spectrum[high_magnitude_indices], 'ro', markersize=5)

            plt.xlim(0, self.RATE / 15)  # Limitar la visualización a frecuencias positivas
            plt.ylim(0, None)  # Limitar la visualización a magnitudes positivas

            # Guardar la imagen si se proporciona un nombre de archivo
            # Guardar la imagen si se proporciona un nombre de archivo
            if save_plot_filename:
                datos_folder = "datos"
                if not os.path.exists(datos_folder):
                    os.makedirs(datos_folder)  # Crea la carpeta "datos" si no existe

                # Crear la subcarpeta con la fecha actual si no existe
                subcarpeta_fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                carpeta_completa = os.path.join(datos_folder, subcarpeta_fecha)
                if not os.path.exists(carpeta_completa):
                    os.makedirs(carpeta_completa)  # Crea la subcarpeta con la fecha actual si no existe

                # Guardar la imagen dentro de la carpeta con la fecha actual
                filename_plot = os.path.join(carpeta_completa, save_plot_filename)
                plt.savefig(filename_plot)

                # Guardar el archivo de audio dentro de la carpeta con la fecha y hora actual
                filename_audio = os.path.join(carpeta_completa, filename)
                os.makedirs(carpeta_completa, exist_ok=True)  # Crear la carpeta si no existe
                os.rename(filename, filename_audio)

            # Imprimir las frecuencias que superan la magnitud de 0.2 dentro del rango de frecuencia especificado
            print("Frecuencias que superan la magnitud de 0.2 dentro del rango de 100 Hz a 2000 Hz:", magnitude_spectrum)
            return magnitude_spectrum
            if not repeat:
                break

    def get_default_input_device_index(self):
        # Devuelve el primer índice de dispositivo
        return 0

# Uso de la clase SoundDetector
detector = SoundDetector()
high_magnitude_freq = detector.record_and_analyze("grabacion.wav", save_plot_filename="spectrogram.png", input_device_index=2, repeat=True)  # Cambia el valor de input_device_index según tu dispositivo
clasificacion = clasificar_frecuencia(high_magnitude_freq)
nombreMosquito=imprimir_clasificacion(clasificacion)