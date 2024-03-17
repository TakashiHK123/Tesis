import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import wave

class SoundDetector:
    def __init__(self):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.RECORD_SECONDS = 5
        self.p = pyaudio.PyAudio()

    def record_and_analyze(self, filename):
        stream = self.p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             input_device_index=2,
                             frames_per_buffer=self.CHUNK)

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

        # Visualización del espectro de magnitud
        plt.figure(figsize=(8, 4))
        plt.plot(fft_freq[:len(fft_freq) // 2], magnitude_spectrum[:len(fft_freq) // 2])
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Magnitud')
        plt.title('Espectro de Magnitud')
        plt.grid(True)
        plt.show()

        self.p.terminate()

# Uso de la clase SoundDetector
detector = SoundDetector()
detector.record_and_analyze("grabacion.wav")
