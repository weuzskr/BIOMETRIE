import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

def extract_photo_from_image(pil_image: Image.Image) -> Image.Image | None:
    """
    Détecte et extrait le visage présent dans une image d'identité.
    Améliore la qualité de l'image extraite (netteté, contraste, luminosité).
    """
    # Convertir PIL image en tableau OpenCV
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Convertir en niveaux de gris
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # Détection de visage
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(faces) == 0:
        return None

    # Coordonnées avec marge
    x, y, w, h = faces[0]
    margin_ratio = 0.35
    margin_x = int(w * margin_ratio)
    margin_y = int(h * margin_ratio)

    x1 = max(0, x - margin_x)
    y1 = max(0, y - margin_y)
    x2 = min(cv_image.shape[1], x + w + margin_x)
    y2 = min(cv_image.shape[0], y + h + margin_y)

    # Extraire le visage
    face_roi = cv_image[y1:y2, x1:x2]

    # Réduction de bruit (optionnelle mais utile)
    denoised_face = cv2.bilateralFilter(face_roi, d=9, sigmaColor=75, sigmaSpace=75)

    # Convertir en image PIL
    pil_face = Image.fromarray(cv2.cvtColor(denoised_face, cv2.COLOR_BGR2RGB))

    # Améliorations de qualité avec PIL
    pil_face = pil_face.convert("RGB")

    # Améliorer la netteté
    pil_face = pil_face.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

    # Améliorer la luminosité et le contraste
    enhancer = ImageEnhance.Contrast(pil_face)
    pil_face = enhancer.enhance(1.2)  # Contraste

    enhancer = ImageEnhance.Brightness(pil_face)
    pil_face = enhancer.enhance(1.1)  # Luminosité

    # Redimensionner à une taille standard (facultatif, ex: 256x256)
    pil_face = pil_face.resize((256, 256), Image.Resampling.LANCZOS)

    print(f"Taille de la photo extraite avec marge et améliorations : {pil_face.size}")
    return pil_face
