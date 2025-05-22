from .electoral_recto import parse_electoral_recto_info
from .electoral_verso import parse_electoral_verso_info

def detect_document_type(raw_text):
    text = raw_text.lower()

    recto_keys = ["date de naissance", "taille", "sexe"]
    verso_keys = ["lieu de vote", "numéro d'électeur", "nin", "bureau", "commune"]

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

def parse_document(raw_text, doc_type=None):
    if not doc_type or doc_type == "auto":
        doc_type = detect_document_type(raw_text)

    if doc_type == "electoral_recto":
        return parse_electoral_recto_info(raw_text)
    elif doc_type == "electoral_verso":
        return parse_electoral_verso_info(raw_text)
    elif doc_type == "electoral_both":
        recto_data = parse_electoral_recto_info(raw_text)
        verso_data = parse_electoral_verso_info(raw_text)
        return {**recto_data, **verso_data}
    else:
        return {}
