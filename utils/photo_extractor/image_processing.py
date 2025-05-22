#from extractor import extract_photo_from_image
from utils.photo_extractor.extractor import extract_photo_from_image
import numpy as np

def prepare_image_for_recognition(file_storage):
    # Convertir FileStorage en PIL Image
    from PIL import Image
    import io

    raw_bytes = file_storage.read()
    img = Image.open(io.BytesIO(raw_bytes))

    # Extraire le visage et améliorer l’image
    pil_face = extract_photo_from_image(img)

    if pil_face is None:
        # Si pas de visage détecté, fallback sur image originale convertie en RGB
        pil_face = img.convert("RGB")

    # Convertir PIL en numpy array RGB pour face_recognition
    img_array = np.array(pil_face)

    # Remettre le curseur au début du fichier pour réutilisation si besoin
    file_storage.seek(0)

    return img_array
