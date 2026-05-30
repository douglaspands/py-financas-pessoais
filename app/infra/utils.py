import unicodedata


def remover_acentos(text: str) -> str:
    if not text:
        return ""

    nfkd = unicodedata.normalize("NFKD", text)
    return nfkd.encode("ASCII", "ignore").decode("utf-8")
