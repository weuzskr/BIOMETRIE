import re

def clean_ocr_errors(text):
    substitutions = [
        ('SIP.', 'S/P'),
        ('SIP ', 'S/P '),
        ('SIP/', 'S/P'),
        ('leu de naissance', 'lieu de naissance'),
        ('le ', ' / '),
        ('lélivrance', 'délivrance'),
        ('dehvrance', 'délivrance'),
        ('I<SEN', '<SEN'),
        ('donmcile', 'domicile'),
        ('donicile', 'domicile'),
        ('domcile', 'domicile'),
        ('dornicile', 'domicile'),
        ('expiratlon', 'expiration'),
        ('délivranoe', 'délivrance'),
        ('naissanoe', 'naissance'),
        ('norn', 'nom'),
        ('prénorn', 'prénom'),
    ]
    for wrong, correct in substitutions:
        text = text.replace(wrong, correct)
    return text

def parse_electoral_recto_info(raw_text):
    raw_text = clean_ocr_errors(raw_text)
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    data = {}

    adresse_detectee = False

    for idx, line in enumerate(lines):
        lower_line = line.lower()

        # Numéro de carte : ligne contenant "carte" ou long chiffre
        if 'carte' in lower_line or re.search(r'\d{5,}', line):
            match = re.search(r'\d[\d\s]{12,}', line.replace('.', ''))
            if match:
                cleaned = re.sub(r'\s+', '', match.group())
                if len(cleaned) >= 14:
                    data['numero_carte'] = cleaned

        # Prénoms + nom détectés en cascade
        elif 'prénom' in lower_line or 'prenoms' in lower_line:
            if idx + 2 < len(lines):
                prenom_line = lines[idx + 1].strip()
                nom_line = lines[idx + 2].strip()
                if prenom_line.isalpha():
                    data['prenom'] = prenom_line.capitalize()
                if nom_line.isalpha():
                    data['nom'] = nom_line.capitalize()

        # Fallback nom seul
        elif 'nom' in lower_line and 'prenom' not in lower_line:
            if idx + 1 < len(lines):
                nom_line = lines[idx + 1].strip()
                if nom_line.isalpha():
                    data['nom'] = nom_line.capitalize()

        # Deux dates sur une ligne
        elif len(re.findall(r'\d{2}/\d{2}/\d{4}', line)) == 2:
            dates = re.findall(r'\d{2}/\d{2}/\d{4}', line)
            data['date_délivrance'] = dates[0]
            data['date_expiration'] = dates[1]

        # Une date avec contexte
        elif re.search(r'\d{2}/\d{2}/\d{4}', line):
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', line)
            previous_line = lines[idx - 1].lower() if idx > 0 else ''
            if 'naissance' in previous_line:
                data['date_naissance'] = date_match.group()
            elif 'expiration' in previous_line:
                data['date_expiration'] = date_match.group()
            elif 'délivrance' in previous_line:
                data['date_delivrance'] = date_match.group()

            sexe_match = re.search(r'\b[MF]\b', line)
            if sexe_match:
                data['sexe'] = sexe_match.group()
            taille_match = re.search(r'(\d{2,3})\s*cm', lower_line)
            if taille_match:
                data['taille'] = taille_match.group(1)

        # Lieu de naissance
        elif 'lieu de naissance' in lower_line:
            if idx + 1 < len(lines):
                data['lieu_naissance'] = lines[idx + 1].strip()

        # Centre d’enregistrement
        elif 's/p' in lower_line or 'centre' in lower_line:
            if idx + 1 < len(lines):
                data['centre_enregistrement'] = lines[idx + 1].strip()

        # Adresse du domicile
        if 'adresse du domicile' in lower_line or re.search(r'adresse\s+du\s+domicile', lower_line):
            adresse_detectee = True
            continue

        if adresse_detectee and line.strip():
            data['adresse'] = line.strip()
            adresse_detectee = False

    return data
