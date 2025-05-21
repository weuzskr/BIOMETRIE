"""from flask import Flask
from flask_login import LoginManager
from starterkit.model.models import User, db
from config import Config
from flask import Blueprint

# Crée l'application Flask
app = Flask(__name__)
app.config.from_object(Config)  # Charge la configuration depuis un objet de configuration

# Initialisation des extensions
db.init_app(app)  # Initialiser SQLAlchemy
login_manager = LoginManager()
login_manager.init_app(app)  # Initialiser Flask-Login

# Configuration du Login Manager
login_manager.login_view = 'auth.signin'  # Redirige vers la page de connexion si l'utilisateur n'est pas connecté

# Fonction pour charger l'utilisateur par son ID (requise par Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Supposant que vous utilisez SQLAlchemy pour gérer les utilisateurs

# Créez le Blueprint pour l'authentification
auth_blueprint = Blueprint('auth', __name__)

# Ajoutez les routes pour l'authentification
@auth_blueprint.route('/signin', methods=['GET', 'POST'])
def signin():
    # Logique de la vue de connexion
    return "Signin page"  # À remplacer par votre logique réelle

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    # Logique de la vue d'inscription
    return "Signup page"  # À remplacer par votre logique réelle

@auth_blueprint.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    # Logique de la vue de réinitialisation de mot de passe
    return "Reset Password page"  # À remplacer par votre logique réelle

@auth_blueprint.route('/new-password', methods=['GET', 'POST'])
def new_password():
    # Logique de la vue de création de nouveau mot de passe
    return "New Password page"  # À remplacer par votre logique réelle

# Enregistrement du Blueprint
app.register_blueprint(auth_blueprint, url_prefix='/api/auth')  # Enregistre le Blueprint sous /api/auth

# Autres configurations (si nécessaire)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Si vous utilisez HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialisation et création de la base de données (facultatif, selon vos besoins)
with app.app_context():
    db.create_all()  # Créer les tables si nécessaire (à ne pas faire en production sans précautions)

# Enregistrement des autres Blueprints ou services ici si nécessaire  """

