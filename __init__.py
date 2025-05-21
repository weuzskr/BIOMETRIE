import logging
import os
from venv import logger
from os.path import dirname
from sys import path
from flask_login import LoginManager
from flask_migrate import Migrate
from .model.models import db, User

path.insert(0, dirname(__file__))
from flask import Flask, session, redirect, url_for

app = Flask(__name__, template_folder='_templates', static_folder='_templates/assets')
app.config.from_object('config.Config')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Désactiver les logs de niveau WARNING
app.logger.setLevel(logging.ERROR)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))  # Utilise la clé de .env
db.init_app(app)
# Initialiser Flask-Migrate
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_RECORD_QUERIES"] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Empêche l'accès aux cookies par JavaScript
app.config['SESSION_COOKIE_SECURE'] = True  # Utilise HTTPS pour les cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Limite les envois inter-sites des cookies

from datetime import timedelta

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)  # Expiration après 30 minutes
from flask_login import current_user

@app.before_request
def make_session_permanent():
    if current_user.is_authenticated:  # Rendre permanent uniquement pour les utilisateurs connectés
        session.permanent = True
    else:
        session.permanent = False


  # Remplacez par votre modèle d'utilisateur

# Import all urls file
import starterkit.dashboards.urls
import starterkit.auth.urls






from starterkit._keenthemes.views import SystemView
from starterkit._keenthemes.settings import settings

from document.urls import documents_bp
#from facesdk_client.client import compare_faces


app.register_blueprint(documents_bp, url_prefix='/documents')

app.register_error_handler(404, SystemView.as_view('Not Found Error', template_name='pages/' + settings.KT_THEME + '/system/error.html', status=404))
app.register_error_handler(500, SystemView.as_view('System Error', template_name='pages/' + settings.KT_THEME + '/system/error.html', status=500))
@app.route('/')
def home():
    return redirect(url_for('signin'))

# Declaration des blueprint



# Enregistrement des blueprint

with app.app_context():
    logger.info("Création des tables dans la base de données...")
    db.create_all()
    logger.info("Tables créées avec succès.")
#if app.config['DEBUG']:
    #print(f"Clé secrète utilisée : {app.config['SECRET_KEY']}")


