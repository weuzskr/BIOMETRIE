def parse_electoral_info(raw_text):
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    data = {}

    for idx, line in enumerate(lines):
        if 'REPUBLIQUE DU SENEGAL' in line:
            data['titre'] = line
        elif "Numero d'électeur" in line:
            data['numero_electeur'] = line.split("Numero d'électeur")[-1].strip()
        elif 'Region' in line and 'Departement' in line:
            # La ligne suivante contient les valeurs
            if idx + 1 < len(lines):
                values = lines[idx + 1].split()
                if len(values) >= 2:
                    data['region'] = values[0]
                    data['departement'] = values[1]
        elif 'Arrondissement' in line:
            if idx + 1 < len(lines):
                data['arrondissement'] = lines[idx + 1]
        elif 'Commune' in line:
            if idx + 1 < len(lines):
                data['commune'] = lines[idx + 1]
        elif 'Bureau' in line:
            # Cherche un nombre dans la même ligne ou celle qui suit
            import re
            match = re.search(r'\b\d{1,2}\b', line)
            if not match and idx + 1 < len(lines):
                match = re.search(r'\b\d{1,2}\b', lines[idx + 1])
            if match:
                data['bureau'] = match.group()
        elif 'Lieu de vote' in line:
            if idx + 1 < len(lines):
                data['lieu_de_vote'] = lines[idx + 1]
        elif 'NIN' in line:
            nin_raw = line.replace('NIN', '').replace(' ', '').strip()
            if len(nin_raw) >= 13 and nin_raw[0] not in ['1', '2']:
                nin_raw = '1' + nin_raw[1:]  # correction automatique si nécessaire
            data['nin'] = nin_raw
        elif '<<' in line:
            data['nom complet'] = line

    # Extraction nom / prénom depuis MRZ
    if 'mrz' in data:
        parts = data['mrz'].split('<<')
        if len(parts) >= 2:
            data['nom'] = parts[0].replace('<', '').strip()
            data['prenom'] = parts[1].replace('<', ' ').strip()

    return data
