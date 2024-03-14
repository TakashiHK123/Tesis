import pyaudio
import wave
import numpy as np
from scipy.fft import fft
import pywt
import librosa
import matplotlib.pyplot as plt

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "audios/output.wav"
micUSB = 2
def grabar_audio():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=micUSB,
                    frames_per_buffer=CHUNK)

    frames = []

    print("Recording...")

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def detectar_frecuencias():
    audio_data, _ = librosa.load(WAVE_OUTPUT_FILENAME, sr=RATE)

    # Calcular la transformada de Fourier
    fft_data = fft(audio_data)

    # Encontrar las frecuencias dominantes
    freqs = np.fft.fftfreq(len(fft_data))
    idx = np.argmax(np.abs(fft_data))
    dominant_freq = freqs[idx]

    print("Frecuencia dominante (FFT):", dominant_freq)

    # Aplicar wavelet
    coeffs = pywt.wavedec(audio_data, 'db4', level=4)

    # Graficar wavelet
    plt.figure(figsize=(10, 6))
    for i, coeff in enumerate(coeffs):
        plt.subplot(len(coeffs), 1, i + 1)
        plt.plot(coeff)
        plt.title(f'Wavelet Coeficiente {i+1}')
        plt.xlabel('Muestras')
        plt.ylabel('Amplitud')
    plt.tight_layout()
    plt.show()

    # Encontrar frecuencias dominantes en los coeficientes de wavelet
    # Realiza cualquier procesamiento adicional según sea necesario
    print("Frecuencias dominantes (Wavelet):")
    # Tu lógica para procesar las frecuencias dominantes con wavelets aquí

if __name__ == "__main__":
    grabar_audio()
    detectar_frecuencias()
