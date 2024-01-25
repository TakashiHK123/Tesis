import cv2

def capturar_foto(ruta_guardado):
    # Inicializar la cámara
    cap = cv2.VideoCapture(0)  # 0 indica el primer dispositivo de video (puede ser 1, 2, etc. dependiendo de la cámara)

    # Capturar un solo fotograma
    ret, frame = cap.read()

    # Guardar la imagen
    cv2.imwrite(ruta_guardado, frame)

    # Liberar la cámara
    cap.release()

if __name__ == "__main__":
    # Ruta donde guardar la imagen
    ruta_imagen = "/ruta/de/tu/carpeta/imagenes/foto.jpg"
    capturar_foto(ruta_imagen)
    print(f"Foto guardada en: {ruta_imagen}")