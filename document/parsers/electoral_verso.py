def parse_electoral_info(raw_text):
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    data = {}

    import re

    for idx, line in enumerate(lines):
        if 'REPUBLIQUE DU SENEGAL' in line:
            data['titre'] = line
        elif "Numero d'électeur" in line:
            data['numero_élécteur'] = line.split("Numero d'électeur")[-1].strip()
        elif 'Région' in line and 'Département' in line:
            if idx + 1 < len(lines):
                values = lines[idx + 1].split()
                if len(values) >= 2:
                    data['région'] = values[0]
                    data['département'] = values[1]
        elif 'Arrondissement' in line and idx + 1 < len(lines):
            data['arrondissement'] = lines[idx + 1].strip()
        elif 'Commune' in line and idx + 1 < len(lines):
            data['commune'] = lines[idx + 1].strip()
        elif 'Bureau' in line:
            match = re.search(r'\b\d{1,2}\b', line)
            if not match and idx + 1 < len(lines):
                match = re.search(r'\b\d{1,2}\b', lines[idx + 1])
            if match:
                data['bureau'] = match.group()
        elif 'Lieu de vote' in line and idx + 1 < len(lines):
            data['lieu_de_vote'] = lines[idx + 1].strip()

        elif 'NIN' in line:
            nin_raw = line.replace('NIN', '').replace(' ', '').strip()
            if len(nin_raw) >= 13:
                if nin_raw[0] not in ['1', '2']:
                    nin_raw = '1' + nin_raw[1:]  # correction automatique
                formatted_nin = f"{nin_raw[0]} {nin_raw[1:4]} {nin_raw[4:8]} {nin_raw[8:13]}"
                data['nin'] = formatted_nin
            else:
                data['nin'] = nin_raw  # ou log d'erreur éventuel
        elif '<<' in line:
            data['nom complet'] = line

    # Extraction nom / prénom depuis MRZ
    if 'mrz' in data:
        parts = data['mrz'].split('<<')
        if len(parts) >= 2:
            data['nom'] = parts[0].replace('<', ' ').strip()
            data['prenom'] = parts[1].replace('<', ' ').strip()

    return data
