
def clean_ocr_errors(text):
    return (text.replace('SIP.', 'S/P')
                .replace('SIP ', 'S/P ')
                .replace('SIP/', 'S/P')
                .replace('le ', ' / ')  # parfois utilisé comme séparateur
                .replace('lélivrance', 'délivrance')
                .replace('dehvrance', 'délivrance')
                .replace('I<SEN', '<SEN')
           )
def parse_electoral_recto_info(raw_text):
    import re

    raw_text = clean_ocr_errors(raw_text)  # Nettoyage préliminaire

    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    data = {}

    for idx, line in enumerate(lines):
        lower_line = line.lower()

        # Numéro de carte : 17 chiffres (ex: 5 19990312 0 00019)
        if 'carte' in lower_line or re.search(r'\d{5,}', line):
            match = re.search(r'\d[\d\s]{15,}', line.replace('.', ''))
            if match:
                cleaned = re.sub(r'\s+', '', match.group())
                if len(cleaned) >= 14:
                    data['numero_carte'] = cleaned

        # Prénom / Nom
        elif idx + 1 < len(lines) and lines[idx].isupper() and lines[idx + 1].isupper():
            data['prénom'] = lines[idx].capitalize()
            data['nom'] = lines[idx + 1].capitalize()

        # Bloc avec 2 dates sur la même ligne
        elif re.findall(r'\d{2}/\d{2}/\d{4}', line) and len(re.findall(r'\d{2}/\d{2}/\d{4}', line)) == 2:
            dates = re.findall(r'\d{2}/\d{2}/\d{4}', line)
            data['date_delivrance'] = dates[0]
            data['date_expiration'] = dates[1]

        # Bloc contenant date de naissance, sexe et taille
        elif re.search(r'\d{2}/\d{2}/\d{4}', line):
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', line)
            previous_line = lines[idx - 1].lower() if idx > 0 else ''
            if 'naissance' in previous_line:
                data['date_naissance'] = date_match.group()
            elif 'expiration' in previous_line:
                data['date_expiration'] = date_match.group()
            elif 'délivrance' in previous_line:
                data['date_delivrance'] = date_match.group()

            # Sexe et taille dans cette même ligne
            sexe_match = re.search(r'\b[MF]\b', line)
            if sexe_match:
                data['sexe'] = sexe_match.group()
            taille_match = re.search(r'(\d{2,3})\s*cm', line.lower())
            if taille_match:
                data['taille'] = taille_match.group(1)

        # Lieu de naissance
        elif 'lieu de naissance' in lower_line or 'leu de naissance' in lower_line:
            if idx + 1 < len(lines):
                data['lieu_naissance'] = lines[idx + 1]

        # Centre d’enregistrement
        elif 's/p' in lower_line or 'centre' in lower_line:
            if idx + 1 < len(lines):
                data['centre_enregistrement'] = lines[idx + 1]

        # Adresse
        # Adresse
        adresse_detectee = False

        for i, line in enumerate(lines):
            lower_line = line.lower().strip()

            # Étape 1 : repérer la ligne qui annonce le champ
            if 'adresse du domicile' in lower_line or re.search(r'adresse\s+du\s+donmcile', lower_line):
                adresse_detectee = True
                continue

            # Étape 2 : si le champ a été détecté, stocker la ligne suivante non vide
            if adresse_detectee and line.strip():
                data['adresse'] = line.strip()
                adresse_detectee = False  # Réinitialiser le flag

    return data
