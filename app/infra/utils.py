import unicodedata


def remover_acentos(text: str) -> str:
    if not text:
        return ""

    nfkd = unicodedata.normalize("NFKD", text)
    return nfkd.encode("ASCII", "ignore").decode("utf-8")


def formatar_moeda(valor: float) -> str:
    return (
        f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )


def texto_capitalizado(texto: str) -> str:
    if not texto:
        return ""
    palavras = texto.split("_")
    palavras_capitalizadas = [palavra.capitalize() for palavra in palavras]
    return " ".join(palavras_capitalizadas)
