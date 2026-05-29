from enum import StrEnum


class TipoConta(StrEnum):
    DEBITO = "debito"
    CREDITO = "credito"
    FINANCIAMENTO = "financiamento"


# Novas categorias para classificar os gastos
class CategoriaTransacao(StrEnum):
    MORADIA = "moradia"  # Para o financiamento, condomínio, luz
    ALIMENTACAO = "alimentacao"
    TRANSPORTE = "transporte"
    LAZER = "lazer"
    SAUDE = "saude"
    REFEICAO = "refeicao"
    EDUCACAO = "educacao"
    VESTUARIO = "vestuario"
    JOGO = "jogo"
    TECNOLOGIA = "tecnologia"
    PROFISSIONAL = "profissional"
    VEICULO = "veiculo"
    OUTROS = "outros"
