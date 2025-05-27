# starterkit/auth/models.py
import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
# Avant (à ne plus faire)
# db = SQLAlchemy()

# Après : importer l'instance partagée
from starterkit.extensions import db


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # ← ajoute cette ligne

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

import uuid
class Personne(db.Model):
    __tablename__ = 'personnes'
    __table_args__ = {'extend_existing': True}  # ← ajoute cette ligne

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = db.Column(db.String, nullable=False)
    prenom = db.Column(db.String, nullable=False)
    sexe = db.Column(db.String, nullable=True)
    taille = db.Column(db.Integer, nullable=True)
    date_naissance = db.Column(db.Date, nullable=True)
    lieu_naissance = db.Column(db.String, nullable=True)

    # Relation 1 à 1 avec CarteIdentite
    carte = relationship("CarteIdentite", back_populates="personne", uselist=False, cascade="all, delete-orphan")

    # Relation 1 à 1 avec Adresse
    adresse = relationship("Adresse", back_populates="personne", uselist=False, cascade="all, delete-orphan")

    # Relation 1 à 1 avec InformationVote (optionnelle : la personne peut ne pas être électeur)
    info_vote = relationship("InformationVote", back_populates="personne", uselist=False, cascade="all, delete-orphan")

    # Relation 1 à N avec Photo (une personne peut avoir plusieurs photos)
    photos = relationship("Photo", back_populates="personne", cascade="all, delete-orphan")


class CarteIdentite(db.Model):
    __tablename__ = 'cartes_identite'
    __table_args__ = {'extend_existing': True}  # ← ajoute cette ligne

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_carte = db.Column(db.String, unique=True, nullable=False)
    nin = db.Column(db.String, unique=True, nullable=True)
    date_delivrance = db.Column(db.Date, nullable=True)
    date_expiration = db.Column(db.Date, nullable=True)

    # Clé étrangère vers Personne
    personne_id = db.Column(db.String(36), ForeignKey('personnes.id'), nullable=False)
    personne = relationship("Personne", back_populates="carte")


class Adresse(db.Model):
    __tablename__ = 'adresses'
    __table_args__ = {'extend_existing': True}  # ← ajoute cette ligne

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Clé étrangère unique : chaque personne a une seule adresse
    personne_id = db.Column(db.String, ForeignKey('personnes.id'), unique=True)
    adresse = db.Column(db.String, nullable=True)
    domicile = db.Column(db.String, nullable=True)

    personne = relationship("Personne", back_populates="adresse")

class InformationVote(db.Model):
    __tablename__ = 'informations_votes'
    __table_args__ = {'extend_existing': True}  # ← ajoute cette ligne

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Clé étrangère unique : chaque personne peut avoir au plus une fiche électorale
    personne_id = db.Column(db.String, ForeignKey('personnes.id'), unique=True)

    # Détails de l’enregistrement électoral (optionnels)
    lieu_vote = db.Column(db.String, nullable=True)
    centre_enregistrement = db.Column(db.String, nullable=True)
    commune = db.Column(db.String, nullable=True)
    arrondissement = db.Column(db.String, nullable=True)
    departement = db.Column(db.String, nullable=True)
    region = db.Column(db.String, nullable=True)
    code_document = db.Column(db.String, nullable=True)

    personne = relationship("Personne", back_populates="info_vote")


class Photo(db.Model):
    __tablename__ = 'photos'
    __table_args__ = {'extend_existing': True}  # ← ajoute cette ligne

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)  # nom du fichier image
    # Origine de la photo (par exemple : 'extraite' ou 'uploadee')
    photo_type = db.Column(db.String(20), nullable=False)        # 'extraite' ou 'uploadee'
    # Clé étrangère vers la personne concernée
    personne_id = db.Column(db.String(36), db.ForeignKey('personnes.id'), nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.UTC)

    personne = db.relationship("Personne", back_populates="photos")

    """
    Cardinalités du modèle :

    - Personne 1 --- 1 CarteIdentite
        → Une personne possède une seule carte d’identité.

    - Personne 1 --- 1 Adresse
        → Une personne est associée à une seule adresse.

    - Personne 1 --- 0..1 InformationVote
        → Une personne peut être inscrite ou non dans le fichier électoral.

    - Personne 1 --- * Photo
        → Une personne peut avoir plusieurs photos (extraites ou uploadées).
    """


class ComparaisonFaciale(db.Model):
    __tablename__ = 'comparaisons_faciales'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    personne_id = db.Column(db.String(36), db.ForeignKey('personnes.id'), nullable=False)
    photo_extraite_id = db.Column(db.String(36), db.ForeignKey('photos.id'), nullable=False)
    photo_uploadee_id = db.Column(db.String(36), db.ForeignKey('photos.id'), nullable=False)
    similarite = db.Column(db.Float, nullable=False)
    correspondance = db.Column(db.Boolean, nullable=False)
    date_comparaison = db.Column(db.DateTime, default=datetime.UTC)

    personne = db.relationship("Personne", backref="comparaisons_faciales")
    photo_extraite = db.relationship("Photo", foreign_keys=[photo_extraite_id])
    photo_uploadee = db.relationship("Photo", foreign_keys=[photo_uploadee_id])
