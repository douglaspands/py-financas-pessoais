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
