"""Language detection - docs 02_CONV Indian languages."""
import re

def detect_language(text: str) -> str:
    """Simple heuristic for Indian languages + en."""
    if not text:
        return "en"
    # Devanagari Hindi/Marathi
    if re.search(r"[\u0900-\u097F]", text):
        # Marathi vs Hindi: check for Marathi specific? fallback to hi
        if "ळ" in text or "अं" in text:
            return "mr"
        return "hi"
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "ta"
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "te"
    if re.search(r"[\u0C80-\u0CFF]", text):
        return "kn"
    if re.search(r"[\u0D00-\u0D7F]", text):
        return "ml"
    if re.search(r"[\u0A80-\u0AFF]", text):
        return "gu"
    if re.search(r"[\u0980-\u09FF]", text):
        return "bn"
    return "en"

def get_language_name(code: str) -> str:
    names = {"en":"English","hi":"Hindi","mr":"Marathi","ta":"Tamil","te":"Telugu","kn":"Kannada","ml":"Malayalam","gu":"Gujarati","bn":"Bengali"}
    return names.get(code, code)
