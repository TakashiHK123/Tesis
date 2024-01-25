import os
import cv2


def configurar_exposicion(camara, valor_exposicion):
    camara.set(cv2.CAP_PROP_EXPOSURE, valor_exposicion)


def capturar_foto(nombre_archivo):
    cap = cv2.VideoCapture(0)

    # Verificar si la cámara está disponible
    if not cap.isOpened():
        print("Error: No se puede acceder a la cámara. ¿Está conectada correctamente?")
        return

    # Ajustar la exposición (puedes experimentar con diferentes valores)
    configurar_exposicion(cap, -1)

    # Crear la carpeta 'imagenes' si no existe
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    carpeta_imagenes = os.path.join(directorio_actual, "imagenes")

    if not os.path.exists(carpeta_imagenes):
        os.makedirs(carpeta_imagenes)

    # Ruta completa de la imagen dentro de la carpeta 'imagenes'
    ruta_imagen = os.path.join(carpeta_imagenes, nombre_archivo)

    ret, frame = cap.read()
    cv2.imwrite(ruta_imagen, frame)
    cap.release()


if __name__ == "__main__":
    nombre_archivo = "foto.jpg"
    capturar_foto(nombre_archivo)
    print(f"Foto guardada en: imagenes/{nombre_archivo}")


