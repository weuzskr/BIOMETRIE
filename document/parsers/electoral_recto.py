import re

def parse_electoral_back_info(raw_text):
    import re
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

        # Bloc contenant date de naissance, sexe et taille
        elif re.search(r'\d{2}/\d{2}/\d{4}', line):
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', line)
            if date_match:
                previous_line = lines[idx - 1].lower() if idx > 0 else ''
                if 'naissance' in previous_line:
                    data['date_naissance'] = date_match.group()
                elif 'expiration' in previous_line:
                    data['date_expiration'] = date_match.group()
                elif 'delivrance' in previous_line or 'dehvrance' in previous_line:
                    data['date_delivrance'] = date_match.group()

            # Chercher sexe et taille aussi dans cette ligne
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

        # Centre
        elif 'sip' in lower_line or 'centre' in lower_line:
            if idx + 1 < len(lines):
                data['centre_enregistrement'] = lines[idx + 1]

        # Adresse
        elif 'gadafaro' in lower_line or re.search(r'\d+\s+à\s+\d+', lower_line):
            data['adresse'] = line

    return data

