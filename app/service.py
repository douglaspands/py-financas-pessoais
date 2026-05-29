import csv
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import typer

from app import repository
from app.context import Context
from app.enum import CategoriaTransacao

# Importando os elementos do seu projeto atual
from app.model import Conta, TipoConta, Transacao


def calcular_fatura(data_compra: date, dia_fechamento: int) -> str:
    if data_compra.day <= dia_fechamento:
        return data_compra.strftime("%Y-%m")
    else:
        ano, mes = data_compra.year, data_compra.month + 1
        if mes > 12:
            mes, ano = 1, ano + 1
        return f"{ano}-{mes:02d}"


def listar_transacoes(ctx: Context, *, mes_filtro: Optional[str] = None) -> dict:
    contas = repository.listar_contas(ctx)
    if not mes_filtro:
        mes_filtro = date.today().strftime("%Y-%m")

    transacoes = repository.listar_transacoes(ctx, mes_filtro=mes_filtro)

    # --- LÓGICA DO RELATÓRIO DO MÊS ---
    total_mes = 0.0
    resumo_categorias = {}
    resumo_contas = {}

    for tx in transacoes:
        total_mes += tx.valor

        # Agrupando por Categoria
        cat_nome = tx.categoria.value.upper()
        resumo_categorias[cat_nome] = resumo_categorias.get(cat_nome, 0.0) + tx.valor

        # Agrupando por Conta/Cartão
        conta_nome = tx.conta.nome
        resumo_contas[conta_nome] = resumo_contas.get(conta_nome, 0.0) + tx.valor

    return {
        "contas": contas,
        "transacoes": transacoes,
        "mes_filtro": mes_filtro,
        "total_mes": total_mes,
        "resumo_categorias": resumo_categorias,
        "resumo_contas": resumo_contas,
    }


def cadastrar_transacao(
    ctx: Context,
    *,
    descricao: str,
    valor: float,
    conta_id: int,
    categoria: CategoriaTransacao,
    parcelas: int,
) -> str:
    conta = repository.obter_conta(ctx, pk=conta_id)
    if not conta:
        raise ValueError(f"Conta com ID {conta_id} não encontrada")

    data_atual = date.today()
    valor_parcela = valor / parcelas

    for i in range(parcelas):
        data_parcela = data_atual + timedelta(days=30 * i)

        if conta.tipo == TipoConta.CREDITO and conta.dia_fechamento:
            fatura = calcular_fatura(data_parcela, conta.dia_fechamento)
        else:
            fatura = data_parcela.strftime("%Y-%m")

        desc_final = f"{descricao} ({i + 1}/{parcelas})" if parcelas > 1 else descricao

        nova_tx = Transacao(
            descricao=desc_final,
            valor=valor_parcela,
            data=data_atual,
            fatura_mes=fatura,
            categoria=categoria,
            conta_id=conta_id,
        )
        repository.criar_transacao(ctx, transacao=nova_tx)

    return fatura


def cadastrar_conta(
    ctx: Context,
    *,
    nome: str,
    tipo: TipoConta,
    limite: float = 0.0,
    dia_fechamento: Optional[int] = None,
    dia_vencimento: Optional[int] = None,
):
    nova_conta = Conta(
        nome=nome,
        tipo=tipo,
        limite_ou_total=limite,
        dia_fechamento=dia_fechamento,
        dia_vencimento=dia_vencimento,
    )
    repository.criar_conta(ctx, conta=nova_conta)


def limpar_transacoes(ctx: Context):
    repository.limpar_transacoes(ctx)


def importar_transacoes_csv(ctx: Context, *, arquivo: Path) -> tuple[int, int]:
    contagem_linhas = 0
    contagem_insercoes = 0

    with open(arquivo, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)

        for linha in leitor:
            contagem_linhas += 1
            try:
                # Parse e validação dos dados do CSV
                descricao = linha["descricao"]
                valor_total = float(linha["valor"])
                parcelas = int(linha.get("parcelas", 1))
                categoria_str = linha.get("categoria", "outros").lower()
                conta_id = int(linha["conta_id"])

                # Valida a categoria com o Enum
                categoria = CategoriaTransacao(categoria_str)

                # Busca a conta para aplicar a regra de fechamento de fatura
                conta = repository.obter_conta(ctx, pk=conta_id)
                if not conta:
                    typer.secho(
                        f"⚠️ Linha {contagem_linhas}: Conta ID {conta_id} não encontrada. Pulando.",
                        fg=typer.colors.YELLOW,
                    )
                    continue

                data_atual = date.today()
                valor_parcela = valor_total / parcelas

                # Aplica a mesma lógica de parcelamento do seu main.py
                for i in range(parcelas):
                    data_parcela = data_atual + timedelta(days=30 * i)

                    if conta.tipo == TipoConta.CREDITO and conta.dia_fechamento:
                        fatura = calcular_fatura(data_parcela, conta.dia_fechamento)
                    else:
                        fatura = data_parcela.strftime("%Y-%m")

                    desc_final = (
                        f"{descricao} ({i + 1}/{parcelas})"
                        if parcelas > 1
                        else descricao
                    )

                    nova_tx = Transacao(
                        descricao=desc_final,
                        valor=valor_parcela,
                        data=data_atual,
                        fatura_mes=fatura,
                        categoria=categoria,
                        conta_id=conta_id,
                    )
                    repository.criar_transacao(ctx, transacao=nova_tx)
                    contagem_insercoes += 1

            except ValueError:
                typer.secho(
                    f"⚠️ Linha {contagem_linhas}: Erro de conversão de valores. Verifique 'valor', 'parcelas' ou 'conta_id'. Pulando.",
                    fg=typer.colors.YELLOW,
                )
                continue

    return contagem_linhas, contagem_insercoes
