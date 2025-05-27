import logging
from fileinput import filename

from PIL import Image
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

from flask import session, redirect, url_for

class UploadView(MethodView):
    def post(self):
        file = request.files.get('document')
        if not file:
            session['upload_result'] = {'error': "Aucun fichier reçu"}
            return redirect(url_for('upload_result'))

        try:
            filename = file.filename.lower()
            ext = os.path.splitext(filename)[1]

            images = []

            if ext == '.pdf':
                # Traitement d'un PDF
                images = convert_from_bytes(file.read())
                if not images:
                    session['upload_result'] = {'error': "PDF illisible"}
                    return redirect(url_for('upload_result'))

            elif ext in ['.jpg', '.jpeg', '.png']:
                # Traitement d'une image
                image = Image.open(file.stream).convert("RGB")
                images = [image]

            else:
                session['upload_result'] = {'error': "Format de fichier non pris en charge"}
                return redirect(url_for('upload_result'))

            # Sauvegarde de la première image
            first_image_filename = f"{uuid.uuid4().hex}.png"
            first_image_path = os.path.join(UPLOAD_FOLDER, first_image_filename)
            images[0].save(first_image_path, "PNG")

            # OCR
            extracted_texts = [pytesseract.image_to_string(img, lang='eng+fra') for img in images]

            # Analyse
            info_recto = {}
            info_verso = {}

            for text in extracted_texts:
                parsed = parse_document(text)
                if any(k in parsed for k in ['date_naissance', 'sexe', 'taille']):
                    info_recto.update(parsed)
                elif any(k in parsed for k in ['numero_electeur', 'lieu_vote', 'commune']):
                    info_verso.update(parsed)

            # Extraction visage
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

            # Stockage dans session
            session['upload_result'] = {
                'filename': file.filename,
                'message': "Fichier reçu et traité avec succès",
                'extracted_text': "\n\n".join(extracted_texts),
                'info_recto': info_recto,
                'info_verso': info_verso,
                'image_url_filename': first_image_filename,
                'portrait_url': portrait_url
            }

            return redirect(url_for('upload_result'))

        except Exception as e:
            print("[ERROR]", str(e))
            session['upload_result'] = {'error': "Erreur lors du traitement : " + str(e)}
            return redirect(url_for('upload_result'))





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

from flask import request, render_template, current_app
from werkzeug.datastructures import FileStorage
import os
import face_recognition

  # à adapter selon ton projet

def prepare_image_for_recognition(file):
    try:
        image = face_recognition.load_image_file(file)
        current_app.logger.info(f"Image chargée. Dimensions : {image.shape}")
        return image
    except Exception as e:
        current_app.logger.error(f"Erreur lors du chargement de l'image : {e}")
        return None

from flask import session, redirect, url_for

@app.route('/compare-faces', methods=['POST'])
def compare_faces():
    uploaded_file = request.files.get('uploaded_photo')
    portrait_url = request.form.get('portrait_url')

    if not uploaded_file or not portrait_url:
        current_app.logger.warning("Fichier uploadé ou portrait manquant.")
        return "Images manquantes", 400

    try:
        filename = os.path.basename(portrait_url)
        doc_photo_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
        current_app.logger.info(f"[COMPARE] Chemin complet de la photo du document : {doc_photo_path}")

        if not os.path.exists(doc_photo_path):
            current_app.logger.error(f"[COMPARE] Fichier introuvable : {doc_photo_path}")
            return f"Fichier introuvable : {doc_photo_path}", 404

        uploaded_img = prepare_image_for_recognition(uploaded_file)
        with open(doc_photo_path, "rb") as f:
            doc_file = FileStorage(stream=f, filename=filename)
            document_img = prepare_image_for_recognition(doc_file)

        if uploaded_img is None or document_img is None:
            current_app.logger.error("[COMPARE] Échec du chargement d'une ou des deux images.")
            return "Erreur lors du chargement des images", 500

        uploaded_locations = face_recognition.face_locations(uploaded_img)
        document_locations = face_recognition.face_locations(document_img)
        current_app.logger.info(
            f"[COMPARE] Visages détectés : uploadée={len(uploaded_locations)}, document={len(document_locations)}")

        if not uploaded_locations or not document_locations:
            current_app.logger.warning("[COMPARE] Aucun visage détecté dans l'une des images.")
            return "Aucun visage détecté dans l'une des images", 400

        uploaded_encodings = face_recognition.face_encodings(uploaded_img, known_face_locations=uploaded_locations)
        document_encodings = face_recognition.face_encodings(document_img, known_face_locations=document_locations)

        if not uploaded_encodings or not document_encodings:
            current_app.logger.warning("[COMPARE] Échec lors de l'encodage des visages.")
            return "Impossible de générer les encodages de visage", 400

        uploaded_encoding = uploaded_encodings[0]
        document_encoding = document_encodings[0]

        results = face_recognition.compare_faces([document_encoding], uploaded_encoding)
        distance = face_recognition.face_distance([document_encoding], uploaded_encoding)[0]
        similarity = (1 - distance) * 100

        current_app.logger.info(f"[COMPARE] Similarité calculée : {similarity:.2f}%")
        current_app.logger.info(f"[COMPARE] Résultat correspondance : {results[0]}")

        # Persistance du résultat
        from starterkit.model.models import ComparaisonFaciale, Photo

        photo_extraite = Photo.query.filter_by(filename=filename, photo_type="extraite").first()
        photo_uploadee = Photo.query.filter_by(filename=uploaded_file.filename, photo_type="uploadee").first()
        current_app.logger.debug(f"[COMPARE] Photo extraite : {photo_extraite}")
        current_app.logger.debug(f"[COMPARE] Photo uploadée : {photo_uploadee}")

        if photo_extraite and photo_uploadee and photo_extraite.personne_id == photo_uploadee.personne_id:
            comparaison = ComparaisonFaciale(
                personne_id=photo_extraite.personne_id,
                photo_extraite_id=photo_extraite.id,
                photo_uploadee_id=photo_uploadee.id,
                similarite=round(similarity, 2),
                correspondance=results[0]
            )
            db.session.add(comparaison)
            db.session.commit()
            current_app.logger.info(f"[COMPARE] Résultat enregistré en base pour personne {photo_extraite.personne_id}")
        else:
            current_app.logger.warning("[COMPARE] Aucune correspondance de photos/personne pour persister le résultat.")

        session['face_result'] = {
            'similarity': round(similarity, 2),
            'match': str(results[0])
        }

        return redirect(url_for('upload_result'))


    except Exception as e:
        current_app.logger.exception(f"[COMPARE] Erreur inattendue : {e}")
        return f"Erreur pendant la comparaison : {e}", 500




@app.route('/compare-faces-result')
def show_face_result():
    result = session.get('face_result')
    if not result:
        return "Aucun résultat à afficher", 400

    upload_data = session.get('upload_result')
    return render_template(
        "html/document/comparison_result.html",
        similarity=result['similarity'],
        match=result['match'],
        upload_data=upload_data
    )


@app.route('/upload-result')
def upload_result():
    result = session.get('upload_result')
    face_result = session.get('face_result')  # récupération du résultat de comparaison
    if not result:
        return render_template("html/document/resultat.html", error="Aucun résultat disponible")
    return render_template("html/document/resultat.html", **result,face_result=face_result )


from flask import request, session, redirect, url_for, jsonify
import json

from services.enrigistrements import enregistrer_personne

@app.route('/enregistrer', methods=['POST'])
def enregistrer_personne_route():
    try:
        info_recto = json.loads(request.form.get('info_recto', '{}'))
        info_verso = json.loads(request.form.get('info_verso', '{}'))
        portrait_url = request.form.get('portrait_url')
        original_image = request.form.get('image_url_filename')

        logging.info(f"Début enregistrement - recto: {info_recto}, verso: {info_verso}, portrait: {portrait_url}, image: {original_image}")

        personne_id = enregistrer_personne(info_recto, info_verso, portrait_url, original_image)

        logging.info(f"Personne enregistrée avec succès : ID = {personne_id}")

        return jsonify({
            'success': True,
            'message': f"Personne enregistrée avec ID : {personne_id}"
        })

    except Exception as e:
        logging.exception("Erreur lors de l'enregistrement de la personne")
        return jsonify({
            'success': False,
            'message': f"Erreur lors de l'enregistrement : {e}"
        })
