import cv2
import numpy as np
from PIL import Image

def extract_photo_from_image(pil_image: Image.Image) -> Image.Image | None:
    """
    Détecte et extrait le visage (photo) présent dans une image d'identité.
    Retourne un objet PIL.Image contenant le visage élargi, ou None si rien n'est trouvé.
    """
    # Convertir PIL image en tableau OpenCV
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Convertir en niveaux de gris pour le traitement
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # Détecteur de visage Haar cascade (pré-entraîné)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Détecter les visages
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(faces) == 0:
        return None

    # Extraire les coordonnées et ajouter une marge autour
    x, y, w, h = faces[0]
    margin_ratio = 0.3  # 20% de marge

    # Calculer les nouvelles coordonnées élargies
    margin_x = int(w * margin_ratio)
    margin_y = int(h * margin_ratio)

    x1 = max(0, x - margin_x)
    y1 = max(0, y - margin_y)
    x2 = min(cv_image.shape[1], x + w + margin_x)
    y2 = min(cv_image.shape[0], y + h + margin_y)

    # Extraire la région élargie
    face_roi = cv_image[y1:y2, x1:x2]

    # Convertir la région extraite en image PIL
    pil_face = Image.fromarray(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))

    print(f"Taille de la photo extraite avec marge : {pil_face.size}")
    return pil_face
