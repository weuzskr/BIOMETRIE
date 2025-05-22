import logging

from starterkit import app

from document.parsers import parse_document
from document.parsers.electoral_recto import parse_electoral_recto_info
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

            # 2. Sauvegarde de la première page (pour affichage)
            first_image_filename = f"{uuid.uuid4().hex}.png"
            first_image_path = os.path.join(UPLOAD_FOLDER, first_image_filename)
            images[0].save(first_image_path, "PNG")

            # 3. OCR sur toutes les pages
            extracted_texts = [pytesseract.image_to_string(img, lang='eng+fra') for img in images]

            # 4. Analyse (parser auto pour chaque page)
            info_recto = {}
            info_verso = {}

            for text in extracted_texts:
                parsed = parse_document(text)  # Appelle `parse_document(raw_text, doc_type=None)`
                # On trie dans recto ou verso selon les clés détectées
                if any(k in parsed for k in ['date_naissance', 'sexe', 'taille']):
                    info_recto.update(parsed)
                elif any(k in parsed for k in ['numero_electeur', 'lieu_vote', 'commune']):
                    info_verso.update(parsed)

            print("[DEBUG] Recto :", info_recto)
            print("[DEBUG] Verso :", info_verso)

            # 5. Extraction du visage depuis la première page (supposée être le recto)
            portrait_url = None
            face_image = extract_photo_from_image(images[0])
            if face_image:
                face_image_filename = f"face_{uuid.uuid4().hex}.png"
                face_image_path = os.path.join(UPLOAD_FOLDER, face_image_filename)
                face_image.save(face_image_path)
                portrait_url = face_image_filename
                print(f"[INFO] Photo de visage extraite : {face_image_path}")
            else:
                print("[WARN] Aucune photo de visage extraite.")

            # 6. Rendu
            return render_template("html/document/resultat.html",
                                   filename=file.filename,
                                   message="Fichier reçu et traité avec succès",
                                   extracted_text="\n\n".join(extracted_texts),
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

#from utils.image_processing import prepare_image_for_recognition
from utils.photo_extractor.image_processing import prepare_image_for_recognition

@app.route('/compare-faces', methods=['POST'])
def compare_faces():
    uploaded_file = request.files.get('uploaded_photo')
    portrait_url = request.form.get('portrait_url')

    if not uploaded_file or not portrait_url:
        return "Images manquantes", 400

    try:
        filename = os.path.basename(portrait_url)
        doc_photo_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)

        if not os.path.exists(doc_photo_path):
            return f"Fichier introuvable : {doc_photo_path}", 404

        # Préparer images pour reconnaissance
        uploaded_img = prepare_image_for_recognition(uploaded_file)

        from werkzeug.datastructures import FileStorage
        with open(doc_photo_path, "rb") as f:
            doc_file = FileStorage(stream=f, filename=filename)
            document_img = prepare_image_for_recognition(doc_file)

        uploaded_encodings = face_recognition.face_encodings(uploaded_img)
        document_encodings = face_recognition.face_encodings(document_img)

        if not uploaded_encodings or not document_encodings:
            return "Aucun visage détecté dans l'une des images", 400

        uploaded_encoding = uploaded_encodings[0]
        document_encoding = document_encodings[0]

        results = face_recognition.compare_faces([document_encoding], uploaded_encoding)
        distance = face_recognition.face_distance([document_encoding], uploaded_encoding)[0]
        similarity = (1 - distance) * 100

        return render_template("html/document/comparison_result.html", similarity=round(similarity, 2), match=results[0])

    except Exception as e:
        return f"Erreur pendant la comparaison : {e}", 500
