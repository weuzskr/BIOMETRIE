import logging

from starterkit import app

from document.parsers import parse_document
from document.parsers.electoral_recto import parse_electoral_back_info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import pytesseract
# Si nécessaire :
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from flask.views import MethodView
from flask import render_template, request
import os
import uuid
from pdf2image import convert_from_bytes
import pytesseract
UPLOAD_FOLDER = '_assets/uploads'
PORTRAIT_FOLDER = '_assets/portraits'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PORTRAIT_FOLDER, exist_ok=True)

from utils.photo_extractor.extractor import extract_photo_from_image

class UploadView(MethodView):
    def post(self):
        file = request.files.get('pdf_file')
        if not file:
            return render_template("html/document/resultat.html", error="Aucun fichier reçu")

        try:
            # 1. Convertir PDF en images
            images = convert_from_bytes(file.read())
            if not images:
                return render_template("html/document/resultat.html", error="PDF illisible")

            # 2. Sauvegarder la première page comme aperçu
            first_image_filename = f"{uuid.uuid4().hex}.png"
            first_image_path = os.path.join(UPLOAD_FOLDER, first_image_filename)
            images[0].save(first_image_path, "PNG")

            # 3. OCR : recto = page 0, verso = page 1 si présent
            recto_text = pytesseract.image_to_string(images[0], lang='eng+fra')
            verso_text = pytesseract.image_to_string(images[1], lang='eng+fra') if len(images) > 1 else ""

            # 4. Analyse du texte (parse)
            info_recto = parse_document(recto_text, doc_type="electoral_recto")
            info_verso = parse_document(verso_text, doc_type="electoral_verso")
            print(" Données extraites du recto :", info_recto)
            print(" Données extraites du verso :", info_verso)

            # 5. Extraction du visage
            portrait_url = None
            face_image = extract_photo_from_image(images[0])
            if face_image:
                face_image_filename = f"face_{uuid.uuid4().hex}.png"
                face_image_path = os.path.join(UPLOAD_FOLDER, face_image_filename)
                face_image.save(face_image_path)
                portrait_url = face_image_filename
                print(f"[INFO] Photo de visage extraite : {face_image_path}")
            else:
                print("[WARN] Aucune photo d'identité extraite du recto.")

            # 6. Rendu final
            return render_template("html/document/resultat.html",
                                   filename=file.filename,
                                   message="Fichier reçu et traité avec succès",
                                   extracted_text=recto_text + "\n\n" + verso_text,
                                   info_verso=info_verso,
                                   info_recto=info_recto,
                                   image_url_filename=first_image_filename,
                                   portrait_url=portrait_url)

        except Exception as e:
            print("[ERROR]", str(e))
            return render_template("html/document/resultat.html", error="Erreur lors du traitement : " + str(e))
from flask import send_from_directory

@app.route('/assets/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('_assets/uploads', filename)

# Enregistrement de la route
upload_view = UploadView.as_view("upload_view")
app.add_url_rule("/upload", view_func=upload_view, methods=["POST"])

from flask import request, render_template
import os


from services.face_compare import compare_faces_sdk

UPLOAD_FOLDER = '_assets/uploads'  # à adapter

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # tu peux aussi utiliser None pour affichage console
    filemode='a'
)

import face_recognition

import os
from flask import current_app

@app.route('/compare-faces', methods=['POST'])
def compare_faces():
    uploaded_file = request.files.get('uploaded_photo')
    portrait_url = request.form.get('portrait_url')  # ex: "_assets/uploads/face_XXX.png"

    if not uploaded_file or not portrait_url:
        return "Images manquantes", 400

    try:
        # Normaliser le chemin reçu (remplacer \ par /)
        portrait_url = portrait_url.replace("\\", "/")

        # Extraire seulement le nom de fichier (ex: face_XXX.png)
        filename = os.path.basename(portrait_url)

        # Construire le chemin absolu complet vers le fichier dans UPLOAD_FOLDER
        doc_photo_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)

        if not os.path.exists(doc_photo_path):
            return f"Fichier introuvable : {doc_photo_path}", 404

        # Chargement des images
        uploaded_image = face_recognition.load_image_file(uploaded_file)
        document_image = face_recognition.load_image_file(doc_photo_path)

        # Encodage facial
        uploaded_encodings = face_recognition.face_encodings(uploaded_image)
        document_encodings = face_recognition.face_encodings(document_image)

        if not uploaded_encodings or not document_encodings:
            return "Aucun visage détecté dans l'une des images", 400

        uploaded_encoding = uploaded_encodings[0]
        document_encoding = document_encodings[0]

        # Calcul de la distance et similarité
        results = face_recognition.compare_faces([document_encoding], uploaded_encoding)
        distance = face_recognition.face_distance([document_encoding], uploaded_encoding)[0]
        similarity = (1 - distance) * 100

        return render_template("html/document/comparison_result.html", similarity=round(similarity, 2), match=results[0])

    except Exception as e:
        return f"Erreur pendant la comparaison : {e}", 500
