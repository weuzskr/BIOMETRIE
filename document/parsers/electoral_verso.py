import re


import re

def parse_electoral_verso_info(raw_text):
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    data = {}

    for idx, line in enumerate(lines):
        lower_line = line.lower()

        # Numéro d'électeur
        if 'electeur' in lower_line:
            match = re.search(r'\d{6,}', line)
            if match:
                data['numero_electeur'] = match.group()

        # Région et Département (souvent sur la même ligne)
        elif 'region' in lower_line and 'departement' in lower_line and idx + 1 < len(lines):
            region_dept = lines[idx + 1].split()
            if len(region_dept) >= 2:
                data['region'] = region_dept[0]
                data['departement'] = region_dept[1]

        # Région seule (fallback)
        elif 'region' in lower_line and idx + 1 < len(lines) and 'region' not in data:
            data['region'] = lines[idx + 1].strip()

        # Département seul (fallback)
        elif 'departement' in lower_line and idx + 1 < len(lines) and 'departement' not in data:
            data['departement'] = lines[idx + 1].strip()

        # Arrondissement
        elif 'arrondissement' in lower_line and idx + 1 < len(lines):
            data['arrondissement'] = lines[idx + 1].strip()

        # Commune
        elif 'commune' in lower_line and idx + 1 < len(lines):
            data['commune'] = lines[idx + 1].strip()

        # Bureau de vote
        elif 'bureau' in lower_line and idx + 1 < len(lines):
            # Nettoyage des symboles OCR (ex: "01 »))")
            bureau_line = re.sub(r'[^\d]', '', lines[idx + 1])
            data['bureau'] = bureau_line if bureau_line else lines[idx + 1].strip()

        # Lieu de vote
        elif 'lieu de vote' in lower_line and idx + 1 < len(lines):
            data['lieu_vote'] = lines[idx + 1].strip()

        # NIN
        elif 'nin' in lower_line:
            # Capture brute
            nin_line = line.strip()

            # Corriger erreur fréquente de l’OCR : "4" mal reconnu au début à la place de "1"
            nin_line = re.sub(r'^(NIN\s+)4', r'\g<1>1', nin_line)

            # Facultatif : valider la forme générale du NIN (en chiffres et espaces)
            if re.search(r'\d[\d\s]{10,}', nin_line):
                data['nin'] = nin_line


        # Centre d'enregistrement : SIP ou S/P
        elif 'sip' in lower_line or 's/p' in lower_line or 'centre' in lower_line:
            data['centre_enregistrement'] = line.replace('SIP', 'S/P').replace('sip', 's/p')

        # MRZ ligne 1 (code)
        elif re.match(r'I<', line):
            data['code'] = line.strip()

        # MRZ ligne 2 (naissance, sexe, expiration)
        elif re.match(r'\d{6}[MF]\d{6}', line):
            mrz = line.strip()
            data['mrz_2'] = mrz
            try:
                naissance = f"{mrz[0:2]}/{mrz[2:4]}/{1900 + int(mrz[4:6])}"
                expiration = f"{mrz[7:9]}/{mrz[9:11]}/{2000 + int(mrz[11:13])}"
                data['date_naissance'] = naissance
                data['sexe'] = 'Masculin' if mrz[6] == 'M' else 'Féminin'
                data['date_expiration'] = expiration
            except Exception as e:
                print(f"[WARN] Erreur extraction MRZ: {e}")

        # MRZ ligne 3 (nom et prénom)
        elif re.match(r'[A-Z]+<<[A-Z]+', line):
            parts = line.strip().split('<<')
            data['nom'] = parts[0].title()
            data['prenom'] = parts[1].replace('<', ' ').title() if len(parts) > 1 else ''

    return data
