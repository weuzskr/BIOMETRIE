# parsing/detect.py

def detect_document_type(raw_text):
    text = raw_text.lower()

    recto_keys = ["date de naissance", "taille", "sexe"]
    verso_keys = ["lieu de vote", "numéro d'électeur", "nin"]

    is_recto = any(k in text for k in recto_keys)
    is_verso = any(k in text for k in verso_keys)

    if is_recto and is_verso:
        return "electoral_both"
    elif is_recto:
        return "electoral_recto"
    elif is_verso:
        return "electoral_verso"
    else:
        return "unknown"
