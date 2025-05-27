import re

def clean_ocr_errors(text):
    return (text.replace('SIP.', 'S/P')
                .replace('SIP ', 'S/P ')
                .replace('SIP/', 'S/P')
                .replace('le ', ' / ')  # parfois utilisé comme séparateur
                .replace('lélivrance', 'délivrance')
                .replace('dehvrance', 'délivrance')
                .replace('I<SEN', '<SEN'))

def parse_electoral_recto_info(raw_text):
    raw_text = clean_ocr_errors(raw_text)
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    data = {}

    adresse_detectee = False

    for idx, line in enumerate(lines):
        lower_line = line.lower()

        # Numéro de carte : 17 chiffres typiquement
        if 'carte' in lower_line or re.search(r'\d{5,}', line):
            match = re.search(r'\d[\d\s]{15,}', line.replace('.', ''))
            if match:
                cleaned = re.sub(r'\s+', '', match.group())
                if len(cleaned) >= 14:
                    data['numero_carte'] = cleaned

        # Détection prénom(s) / nom sur plusieurs lignes
        elif 'prénom' in lower_line or 'prenoms' in lower_line:
            # Cas où les valeurs sont sur les lignes suivantes
            if idx + 2 < len(lines):
                prenom_line = lines[idx + 1].strip()
                nom_line = lines[idx + 2].strip()

                # S'assure que ce sont bien des noms valides
                if prenom_line.isalpha() and nom_line.isalpha():
                    data['prenom'] = prenom_line.capitalize()
                    data['nom'] = nom_line.capitalize()

        # Fallback : "Nom" détecté seul
        elif 'nom' in lower_line and 'prenom' not in lower_line:
            if idx + 1 < len(lines):
                nom_line = lines[idx + 1].strip()
                if nom_line.isalpha():
                    data['nom'] = nom_line.capitalize()

        # Deux dates sur la même ligne
        elif re.findall(r'\d{2}/\d{2}/\d{4}', line) and len(re.findall(r'\d{2}/\d{2}/\d{4}', line)) == 2:
            dates = re.findall(r'\d{2}/\d{2}/\d{4}', line)
            data['date_delivrance'] = dates[0]
            data['date_expiration'] = dates[1]

        # Une date seule avec contexte
        elif re.search(r'\d{2}/\d{2}/\d{4}', line):
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', line)
            previous_line = lines[idx - 1].lower() if idx > 0 else ''
            if 'naissance' in previous_line:
                data['date_naissance'] = date_match.group()
            elif 'expiration' in previous_line:
                data['date_expiration'] = date_match.group()
            elif 'délivrance' in previous_line:
                data['date_delivrance'] = date_match.group()

            # Sexe et taille
            sexe_match = re.search(r'\b[MF]\b', line)
            if sexe_match:
                data['sexe'] = sexe_match.group()
            taille_match = re.search(r'(\d{2,3})\s*cm', lower_line)
            if taille_match:
                data['taille'] = taille_match.group(1)

        # Lieu de naissance
        elif 'lieu de naissance' in lower_line or 'leu de naissance' in lower_line:
            if idx + 1 < len(lines):
                data['lieu_naissance'] = lines[idx + 1].strip()

        # Centre d’enregistrement
        elif 's/p' in lower_line or 'centre' in lower_line:
            if idx + 1 < len(lines):
                data['centre_enregistrement'] = lines[idx + 1].strip()

        # Adresse du domicile
        if 'adresse du domicile' in lower_line or re.search(r'adresse\s+du\s+donmcile', lower_line):
            adresse_detectee = True
            continue

        if adresse_detectee and line.strip():
            data['adresse'] = line.strip()
            adresse_detectee = False

    return data
