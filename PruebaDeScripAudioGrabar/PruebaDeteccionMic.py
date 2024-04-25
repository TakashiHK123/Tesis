import pyaudio

def listar_dispositivos():
    p = pyaudio.PyAudio()
    num_dispositivos = p.get_device_count()
    for i in range(num_dispositivos):
        info = p.get_device_info_by_index(i)
        print("Dispositivo {}: {}, {} canales de entrada".format(i, info['name'], info['maxInputChannels']))

def seleccionar_mic_usb_deseado():
    p = pyaudio.PyAudio()
    num_dispositivos = p.get_device_count()
    for i in range(num_dispositivos):
        info = p.get_device_info_by_index(i)
        if "micrófono USB" in info["name"].lower():
            print("Seleccionando micrófono USB: {}".format(info['name']))
            return i
    return None

def grabar_audio():
    p = pyaudio.PyAudio()
    dispositivo_usb = seleccionar_mic_usb_deseado()
    if dispositivo_usb is not None:
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        input_device_index=dispositivo_usb,
                        frames_per_buffer=1024)
        frames = []
        print("Grabando...")
        for _ in range(0, int(44100 / 1024 * 5)):  # Grabar durante 5 segundos
            data = stream.read(1024)
            frames.append(data)
        print("Grabación finalizada.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open("audios/output.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()
    else:
        print("No se encontró un micrófono USB.")

if __name__ == "__main__":
    listar_dispositivos()
    grabar_audio()
