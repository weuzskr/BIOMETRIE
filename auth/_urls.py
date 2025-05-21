"""from flask import session, redirect
from flask_login import LoginManager

from starterkit import app
from flask_login import LoginManager
from .signin.views import AuthSigninView
from .signup.views import AuthSignupView
from .reset_password.views import AuthResetPasswordView
from .new_password.views import AuthNewPasswordView
from ..model.models import User



# Définition des routes
app.add_url_rule('/signin', view_func=AuthSigninView.as_view('signin'))
app.add_url_rule('/signup', view_func=AuthSignupView.as_view('signup'))
app.add_url_rule('/reset-password', view_func=AuthResetPasswordView.as_view('reset-password'))
app.add_url_rule('/new-password', view_func=AuthNewPasswordView.as_view('new-password'))

# Configuration du login manager
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Supposant que vous utilisez SQLAlchemy pour les utilisateurs

app.route('/logout')
def logout():
    session.clear()  # Vide la session pour déconnecter l'utilisateur
    return redirect('/signin')  # Redirige vers la page de connexion  """
