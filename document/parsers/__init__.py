from .electoral import parse_electoral_info
from .electoral_back import parse_electoral_back_info

def parse_document(raw_text, doc_type):
    if doc_type == "electoral":
        return parse_electoral_info(raw_text)
    elif doc_type == "electoral_back":
        return parse_electoral_back_info(raw_text)
    else:
        return {}
