import numpy as np
import scipy.io.wavfile as wav
import alsaaudio
import time
import pyudev
import matplotlib.pyplot as plt


# Inicializar el gráfico
plt.ion()  # Habilitar modo interactivo
fig, ax = plt.subplots()
line, = ax.plot([], [])
ax.set_title('FFT en tiempo real')
ax.set_xlabel('Frecuencia (Hz)')
ax.set_ylabel('Amplitud')
#frecuencias = np.fft.fftfreq(512, 1 / 44100)  # Ajustar según el tamaño del periodo
ax.set_xlim(0,  2000)  # Ajustar según la frecuencia de muestreo
ax.set_ylim(-1800000, 1800000)
longitud_senal = 1024 #Tamanho del bufer de lectura
frecuencia_muestreo = 44100 # Establecer la frecuencia de muestreo a 42.667 kHz
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

def configurar_mic():
    dispositivos_usb = obtener_dispositivos_usb()
    if not dispositivos_usb:
        #print("No se encontraron dispositivos USB.")
        return None
    #print("Dispositivos USB encontrados:")
    #for i, dispositivo in enumerate(dispositivos_usb, 1):
        #print(f'{i}.{dispositivo}')
        
    seleccion = int(2)
    
    if 1 <= seleccion <= len(dispositivos_usb):
        
        # Configurar el micrófono seleccionado con 1 canal (mono)
        mic_configurado = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, cardindex=2)  # Reemplaza 2 con tu cardindex
        mic_configurado.setchannels(1)  # Establecer el número de canales a 1 (mono)
        mic_configurado.setrate(frecuencia_muestreo)  # Establecer la frecuencia de muestreo a 44.1 kHz
        mic_configurado.setformat(alsaaudio.PCM_FORMAT_S16_LE)  # Establecer el formato de audio a 16 bits little-endian

        # Intenta con un tamaño de periodo más pequeño
        mic_configurado.setperiodsize(longitud_senal)  # Establecer el tamaño del periodo

        # Capturar datos
        return mic_configurado
    else:
        print("Seleccion no valida")
        return None 

def detectar_frecuencia_usb(capturador):
    
    
    #Aplicar la Transformada Rapida de Fourier (FFT)
    
    umbral_db = -50
    plt.show(block=False)
    frecuencias = np.fft.fftfreq(longitud_senal, 1 / frecuencia_muestreo)
    amplitudes_iniciales = np.zeros(longitud_senal)
    line, = ax.plot(frecuencias, amplitudes_iniciales)
    try:
        while True:
            
             #Leer datos del microfono USB
            longitud_buffer = len(capturador.read()[1])
            longitud_buffer = longitud_buffer - (longitud_buffer % 2)

            # Procesar los datos capturados
            datos = np.frombuffer(capturador.read()[1][:longitud_buffer], dtype=np.int16)
            # Realizar la FFT
            # Calcular nivel de decibelios RMS
            if datos is not None: 
                rms_level_db = 20 * np.log10(np.sqrt(np.mean(datos**2)))
                # Calcular las frecuencias correspondientes
                fft_resultado = np.fft.fft(datos)
                
                #Calcular las frecuencias correspondientes
                frecuencias = np.fft.fftfreq(longitud_senal, 1/frecuencia_muestreo)
                
                #Encontrar el indice de la frecuencia dominante
                indice_frecuencia_dominante = np.argmax(np.abs(fft_resultado))
                
                #Obtener la frecuencia dominante en Hz
                # Actualizar la línea en el gráfico
                line.set_xdata(np.abs(frecuencias))
                line.set_ydata(fft_resultado)
                #print(np.abs(fft_resultado))
                plt.draw()
                # Actualizar el gráfico
                plt.pause(0.001)  # Añadi un pequeño retraso para permitir la actualización de la interfaz gráfica
                frecuencia_dominante = frecuencias[indice_frecuencia_dominante]
                if frecuencia_dominante != 0 and frecuencia_dominante >=300 and rms_level_db > umbral_db and frecuencia_dominante <=1000:
                    print(f'Decibelios:{rms_level_db}')
                    print(f'Frecuencia: {frecuencia_dominante} Hz')
                    time.sleep(0.01)
                #return frecuencia_dominante
    except KeyboardInterrupt:
         pass
    finally:
        # Cerrar el micrófono al finalizar
        mic_configurado.close()
        plt.ioff()  # Desactivar el modo interactivo de Matplotlib
        plt.show(block=True)  # Esperar a que se cierre la ventana antes de finalizar
#Configurar el microfono fuera de la funcion
mic_configurado = configurar_mic()
    #Ejecutar el detector de frecuencia con la configuracion del microfono
detectar_frecuencia_usb(mic_configurado)
