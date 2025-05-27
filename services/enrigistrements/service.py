from flask import current_app
from starterkit.model.models import  Personne, CarteIdentite, Photo, Adresse, InformationVote
import uuid
from starterkit.extensions import db
from datetime import datetime

def enregistrer_personne(info_recto: dict, info_verso: dict, portrait_url: str, original_image: str):
    """Insère une personne dans la base de données à partir des informations extraites."""
    personne = Personne(
        id=str(uuid.uuid4()),
        nom=info_verso.get("nom", "INCONNU"),
        prenom=info_verso.get("prenom", "INCONNU"),
        sexe=info_recto.get("sexe"),
        taille=info_recto.get("taille"),
        date_naissance=info_recto.get("date_naissance"),
        lieu_naissance=info_recto.get("lieu_naissance")
    )

    personne.carte = CarteIdentite(
        numero_carte=info_recto.get("numero_carte"),
        nin=info_recto.get("nin"),
        date_delivrance=info_recto.get("date_delivrance"),
        date_expiration=info_recto.get("date_expiration")
    )

    personne.adresse = Adresse(
        adresse=info_recto.get("adresse"),
        domicile=info_recto.get("domicile")
    )

    if info_verso:
        personne.info_vote = InformationVote(
            lieu_vote=info_verso.get("lieu_vote"),
            centre_enregistrement=info_verso.get("centre_enregistrement"),
            commune=info_verso.get("commune"),
            arrondissement=info_verso.get("arrondissement"),
            departement=info_verso.get("departement"),
            region=info_verso.get("region"),
            code_document=info_verso.get("code_document")
        )

    if portrait_url:
        personne.photos.append(
            Photo(
                filename=portrait_url,
                photo_type="extraite",
                date_ajout=datetime.utcnow()
            )
        )

    if original_image:
        personne.photos.append(
            Photo(
                filename=original_image,
                photo_type="uploadee",
                date_ajout=datetime.utcnow()
            )
        )

    # 👇 Ajout important : Exécution dans le contexte d'application
    with current_app.app_context():
        db.session.add(personne)
        db.session.commit()
        return personne.id


