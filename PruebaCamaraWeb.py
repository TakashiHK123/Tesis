import cv2

def mostrar_video(camara_index=0):
    cap = cv2.VideoCapture(camara_index)

    if not cap.isOpened():
        print("Error: No se puede acceder a la cámara. ¿Está conectada correctamente?")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error al leer el fotograma")
            break

        cv2.imshow('Video de la cámara', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Cambia el índice de la cámara si tienes más de una conectada.
# Por defecto, se toma la primera cámara (índice 0).
mostrar_video()