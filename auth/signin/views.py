import logging
from flask import render_template, request, redirect, url_for, flash, session
from flask.views import View
from flask_login import login_user
from starterkit.model.models import User
from starterkit.extensions import db


# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # ou INFO en production
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AuthSigninView(View):
    methods = ['GET', 'POST']
    template_name = 'html/auth-login-basic.html'

    def dispatch_request(self):

        if request.method == 'POST':

            logger.debug("Tentative de connexion détectée.")

            identifiant = request.form.get('email-username')
            password = request.form.get('password')

            logger.debug(f"Identifiant reçu : {identifiant}")

            from flask import current_app

            with current_app.app_context():
                user = User.query.filter(
                    (User.email == identifiant) | (User.username == identifiant)
                ).first()

            if user and user.check_password(password):
                login_user(user)
                logger.info(f"Connexion réussie pour l'utilisateur : {user.username}")
                flash('Connexion réussie', 'success')
                return redirect(url_for('dashboard'))  # adapte ce nom à ton blueprint
            else:
                logger.warning("Échec de connexion : identifiant ou mot de passe incorrect.")
                flash('Email/Username ou mot de passe incorrect', 'danger')

        return render_template(self.template_name, title='Connexion')
