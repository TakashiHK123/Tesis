import numpy as np
import matplotlib.pyplot as plt
import alsaaudio
import pyudev

def es_dispositivo_usb(dispositivo):
    # Verificar si el directorio del dispositivo contiene "usb"
    return "usb" in dispositivo.device_path
def obtener_dispositivos_usb():
    context = pyudev.Context()
    dispositivos_usb = []

    for dispositivo in context.list_devices(subsystem='sound'):
        #print("Atributos disponibles para el dispositivo:")
        for atributo in dir(dispositivo.attributes):
            if not atributo.startswith('_'):
                valor = getattr(dispositivo.attributes, atributo)
                #print(f"{atributo}: {valor}")

        devtype = dispositivo.attributes.get('DEVTYPE')
        id_bus = dispositivo.attributes.get('ID_BUS')

        #print(f"devtype: {devtype}")
        #print(f"id_bus: {id_bus}")

        # Comprobamos si el dispositivo está en el bus USB
        if es_dispositivo_usb(dispositivo):
            dispositivos_usb.append(dispositivo.device_node)
            print("Este es un dispositivo USB de audio.")
        else:
            print("Este no es un dispositivo USB de audio.")

        print("\n---\n")

    return dispositivos_usb

def inicializar_microfono():
    #dispositivos_usb = obtener_dispositivos_usb()
    #if not dispositivos_usb:
        #print("No se encontraron dispositivos USB.")
        #return None
    try:
        mic_configurado = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, cardindex=2)
        mic_configurado.setchannels(1)  # Establecer el número de canales a 1 (mono)
        mic_configurado.setrate(44100)  # Establecer la frecuencia de muestreo a 44.1 kHz
        mic_configurado.setformat(alsaaudio.PCM_FORMAT_S16_LE)  # Establecer el formato de audio a 16 bits little-endian
        mic_configurado.setperiodsize(256)  # Establecer el tamaño del periodo
        return mic_configurado
    except alsaaudio.ALSAAudioError as e:
        print(f"Error al inicializar el micrófono: {e}")
        return None

# Inicializar el micrófono
mic_configurado = inicializar_microfono()

# Verificar que la inicialización fue exitosa
if mic_configurado:
    # Inicializar el gráfico
    plt.ion()  # Habilitar modo interactivo
    fig, ax = plt.subplots()
    line, = ax.plot([], [])
    ax.set_title('FFT en tiempo real')
    ax.set_xlabel('Frecuencia (Hz)')
    ax.set_ylabel('Amplitud')
    frecuencias = np.fft.fftfreq(256, 1 / 44100)  # Ajustar según el tamaño del periodo
    ax.set_xlim(0, 22050)  # Ajustar según la frecuencia de muestreo

    try:
        # Bucle infinito para actualizar la imagen
        while True:
            
            # Capturar datos
            captura = mic_configurado.read()
            datos = np.frombuffer(captura[1], dtype=np.int16)

            # Realizar la FFT
            fft_resultado = np.fft.fft(datos)

            # Actualizar la línea en el gráfico
            line.set_xdata(frecuencias)
            line.set_ydata(np.abs(fft_resultado))

            # Actualizar el gráfico
            plt.pause(0.01)  # Añadir un pequeño retraso para permitir la actualización de la interfaz gráfica

    except KeyboardInterrupt:
        # Capturar Ctrl+C para terminar el bucle
        pass
    finally:
        # Cerrar el gráfico al salir
        plt.ioff()
        plt.show()

    # Cerrar el micrófono al finalizar
    mic_configurado.close()
else:
    print("La inicialización del micrófono ha fallado. Verifica la configuración.")