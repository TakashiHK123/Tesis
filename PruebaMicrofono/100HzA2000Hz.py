import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import wave

class SoundDetector:
    def __init__(self):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 512
        self.RECORD_SECONDS = 5
        self.p = pyaudio.PyAudio()

    def record_and_analyze(self, filename, input_device_index=None):
        if input_device_index is None:
            input_device_index = self.get_default_input_device_index()

        stream = self.p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK,
                             input_device_index=input_device_index)

        print("Grabando...")

        frames = []
        data = []

        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            audio_data = stream.read(self.CHUNK)
            frames.append(audio_data)
            data.extend(np.frombuffer(audio_data, dtype=np.int16))

        print("Fin de la grabación.")

        stream.stop_stream()
        stream.close()

        # Guardar los datos de audio en un archivo WAV
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Procesamiento de los datos grabados
        data = np.array(data)

        fft_data = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(len(data), 1 / self.RATE)
        magnitude_spectrum = np.abs(fft_data)

        # Identificar frecuencias que superan la magnitud de 1 de manera eficiente
        high_magnitude_indices = np.where((magnitude_spectrum > 1) & (fft_freq >= 100) & (fft_freq <= 2000))[0]
        high_magnitude_freq = fft_freq[high_magnitude_indices]

        # Visualización del espectro de magnitud
        plt.figure(figsize=(8, 4))
        plt.plot(fft_freq[:len(fft_freq) // 2], magnitude_spectrum[:len(fft_freq) // 2])
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Magnitud')
        plt.title('Espectro de Magnitud')
        plt.grid(True)

        # Resaltar las frecuencias que superan la magnitud de 1 dentro del rango de frecuencia especificado
        plt.plot(high_magnitude_freq, magnitude_spectrum[high_magnitude_indices], 'ro', markersize=5)

        plt.xlim(0, self.RATE / 2)  # Limitar la visualización a frecuencias positivas
        plt.ylim(0, None)  # Limitar la visualización a magnitudes positivas
        plt.show()

        # Imprimir las frecuencias que superan la magnitud de 1 dentro del rango de frecuencia especificado
        print("Frecuencias que superan la magnitud de 1 dentro del rango de 100 Hz a 2000 Hz:", high_magnitude_freq)

        self.p.terminate()

    def get_default_input_device_index(self):
        return self.p.get_default_input_device_info()["index"]

# Uso de la clase SoundDetector
detector = SoundDetector()
detector.record_and_analyze("grabacion.wav", input_device_index=2)  # Cambia el valor de input_device_index según tu dispositivo
