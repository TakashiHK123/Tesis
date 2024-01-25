import os
import cv2

def capturar_foto(nombre_archivo):
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_imagen = os.path.join(directorio_actual, nombre_archivo)

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite(ruta_imagen, frame)
    cap.release()

if __name__ == "__main__":
    nombre_archivo = "foto.jpg"
    capturar_foto(nombre_archivo)
    print(f"Foto guardada en: {nombre_archivo}")