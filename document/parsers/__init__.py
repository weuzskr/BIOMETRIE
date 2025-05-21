from .electoral_verso import parse_electoral_info
from .electoral_recto import parse_electoral_back_info

def parse_document(raw_text, doc_type):
    if doc_type == "electoral_verso":
        return parse_electoral_info(raw_text)
    elif doc_type == "electoral_recto":
        return parse_electoral_back_info(raw_text)
    else:
        return {}
