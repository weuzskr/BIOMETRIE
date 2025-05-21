from flask import Flask
from model.models import db, User
from config import Config  # Assure-toi que ce fichier s'appelle config.py

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Création d’un utilisateur
with app.app_context():
    db.create_all()  # crée les tables si elles n'existent pas

    # Vérifie si l'utilisateur existe déjà
    if not User.query.filter_by(username='admin').first():
        user = User(
            username='admin',
            email='admin@example.com'
        )
        user.set_password('MotDePasseFort123')

        db.session.add(user)
        db.session.commit()

        print("Utilisateur inséré avec succès.")
    else:
        print("Utilisateur déjà existant.")
