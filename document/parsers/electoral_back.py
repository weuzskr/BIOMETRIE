import re

def parse_electoral_back_info(raw_text):
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    data = {}

    for idx, line in enumerate(lines):
        lower_line = line.lower()

        # Numéro de carte : rechercher une séquence longue de chiffres dans les premières lignes
        if 'carte' in lower_line or re.search(r'\d{5,}', line):
            match = re.search(r'\d{8,}', line)
            if match:
                data['numero_carte'] = match.group()

        # Prénom / Nom
        if idx + 1 < len(lines):
            if lines[idx].isupper() and lines[idx + 1].isupper():
                data['prenom'] = lines[idx].capitalize()
                data['nom'] = lines[idx + 1].capitalize()

        # Date de naissance
        if re.search(r'\d{2}/\d{2}/\d{4}', line):
            data['date_naissance'] = re.search(r'\d{2}/\d{2}/\d{4}', line).group()

        # Sexe
        if re.match(r'^[MF]$', line):
            data['sexe'] = line

        # Taille
        if 'cm' in line.lower():
            match = re.search(r'(\d{2,3})\s*cm', line.lower())
            if match:
                data['taille'] = match.group(1)

        # Lieu de naissance
        if 'lieu de naissance' in lower_line or 'leu de naissance' in lower_line:
            if idx + 1 < len(lines):
                data['lieu_naissance'] = lines[idx + 1]

        # Date de délivrance
        if 'delivrance' in lower_line or 'dehvrance' in lower_line:
            if idx + 1 < len(lines):
                data['date_delivrance'] = lines[idx + 1]

        # Date d'expiration
        if 'expiration' in lower_line:
            if idx + 1 < len(lines):
                match = re.search(r'\d{2}/\d{2}/\d{4}', lines[idx + 1])
                if match:
                    data['date_expiration'] = match.group()

        # Centre d'enregistrement
        if 'sip' in lower_line or 'centre' in lower_line:
            if idx + 1 < len(lines):
                data['centre_enregistrement'] = lines[idx + 1]

        # Adresse
        if 'gadafaro' in lower_line or re.search(r'\d+\s+à\s+\d+', lower_line):
            data['adresse'] = line

    return data
