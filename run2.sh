#!/bin/bash

# Vérifier si Python est installé
if ! command -v python &> /dev/null
then
    echo "Error: Python is not installed. Please install Python."
    exit 1
fi

# Vérifier si le répertoire de l'environnement virtuel existe
if [ ! -d ".venv" ]; then
    echo "Creating a virtual environment..."
    python -m venv .venv
fi

# Activer l'environnement virtuel
source .venv/bin/activate

# Mettre à jour pip (optionnel)
 python -m pip install --upgrade pip

# Installer les dépendances (optionnel)
 python -m pip install -r requirements.txt


# Définir l'environnement Flask et lancer l'application Flask en mode debug
echo "Running Flask app in debug mode..."
export FLASK_ENV=development
flask --app __init__ run --host=0.0.0.0 --port=5000 --debug
