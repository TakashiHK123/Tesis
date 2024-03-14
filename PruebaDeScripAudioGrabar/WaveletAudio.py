import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import pywt
from scipy.fft import fft

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "audios/output.wav"

def listar_dispositivos():
    p = pyaudio.PyAudio()
    num_dispositivos = p.get_device_count()
    for i in range(num_dispositivos):
        info = p.get_device_info_by_index(i)
        print(f"Dispositivo {i}: {info['name']}, {info['maxInputChannels']} canales de entrada")

def seleccionar_mic_usb_deseado():
    p = pyaudio.PyAudio()
    num_dispositivos = p.get_device_count()
    for i in range(num_dispositivos):
        info = p.get_device_info_by_index(i)
        if "micrófono USB" in info["name"].lower():  # Ajusta este criterio según el nombre del dispositivo
            print(f"Seleccionando micrófono USB: {info['name']}")
            return i
    return None

def grabar_audio():
    p = pyaudio.PyAudio()
    dispositivo_usb = seleccionar_mic_usb_deseado()
    if dispositivo_usb is not None:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=dispositivo_usb,
                        frames_per_buffer=CHUNK)

        frames = []

        print("Grabando...")

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Grabación finalizada.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    else:
        print("No se encontró un micrófono USB.")

def detectar_frecuencias():
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
    audio_data = wf.readframes(wf.getnframes())
    audio_data = np.frombuffer(audio_data, dtype=np.int16)

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
    listar_dispositivos()
    grabar_audio()
    detectar_frecuencias()
