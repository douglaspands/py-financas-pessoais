import csv
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import typer

from app.account import service as account_service
from app.account.enum import TipoContaEnum
from app.infra import utils
from app.infra.context import Context
from app.transaction import repository
from app.transaction.enum import CategoriaTransacaoEnum
from app.transaction.model import Transacao


def calcular_fatura(data_compra: date, dia_fechamento: int) -> str:
    if data_compra.day < dia_fechamento:
        return data_compra.strftime("%Y-%m")
    else:
        ano, mes = data_compra.year, data_compra.month + 1
        if mes > 12:
            mes, ano = 1, ano + 1
        return f"{ano}-{mes:02d}"


def proxima_data(data: date, dia: int) -> date:
    try:
        nova_data = data.replace(month=data.month + 1, day=dia)
    except BaseException:
        nova_data = (data.replace(month=data.month + 2, day=1)) - timedelta(days=1)
    return nova_data


async def listar_transacoes(ctx: Context, *, mes_filtro: Optional[str] = None) -> dict:
    contas = await account_service.listar_contas(ctx)
    if not mes_filtro:
        mes_filtro = date.today().strftime("%Y-%m")

    transacoes = await repository.listar_transacoes(ctx, mes_filtro=mes_filtro)

    # --- LÓGICA DO RELATÓRIO DO MÊS ---
    total_mes = 0.0
    resumo_categorias = {}
    resumo_contas = {}

    for tx in transacoes:
        total_mes += tx.valor

        cat_nome = tx.categoria.value.upper()
        resumo_categorias[cat_nome] = resumo_categorias.get(cat_nome, 0.0) + tx.valor

        conta_nome = tx.conta.nome
        resumo_contas[conta_nome] = resumo_contas.get(conta_nome, 0.0) + tx.valor

    return {
        "contas": contas,
        "transacoes": transacoes,
        "mes_filtro": mes_filtro,
        "total_mes": total_mes,
        "resumo_categorias": dict(
            sorted(resumo_categorias.items(), key=lambda item: item[1], reverse=True)
        ),
        "resumo_contas": resumo_contas,
    }


async def cadastrar_transacao(
    ctx: Context,
    *,
    descricao: str,
    valor: float,
    conta_id: int,
    categoria: CategoriaTransacaoEnum,
    parcelas: int,
) -> str:
    conta = await account_service.obter_conta(ctx, pk=conta_id)
    if not conta:
        raise ValueError(f"Conta com ID {conta_id} não encontrada")

    data_atual = date.today()
    dia = data_atual.day
    valor_parcela = valor / parcelas

    data_parcela = data_atual
    for i in range(parcelas):
        data_parcela = data_parcela if i == 0 else proxima_data(data_parcela, dia)

        if conta.tipo == TipoContaEnum.CREDITO and conta.dia_fechamento:
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
        await repository.criar_transacao(ctx, transacao=nova_tx)

    return fatura


async def limpar_transacoes(ctx: Context):
    await repository.limpar_transacoes(ctx)


async def importar_transacoes_csv(ctx: Context, *, arquivo: Path) -> tuple[int, int]:
    contagem_linhas = 0
    contagem_insercoes = 0

    with open(arquivo, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)

        for linha in leitor:
            contagem_linhas += 1
            try:
                descricao = linha["descricao"]
                valor_total = float(str(linha["valor"]).replace(",", "."))
                parcelas = int(linha.get("parcelas", 1))
                categoria_str = utils.remover_acentos(
                    linha.get("categoria", "outros").lower()
                )
                conta_id = int(linha["conta_id"])

                categoria = CategoriaTransacaoEnum(categoria_str)
                conta = await account_service.obter_conta(ctx, pk=conta_id)
                if not conta:
                    typer.secho(
                        f"⚠️ Linha {contagem_linhas}: Conta ID {conta_id} não encontrada. Pulando.",
                        fg=typer.colors.YELLOW,
                    )
                    continue

                data_atual = (
                    datetime.strptime(linha["data"], r"%Y-%m-%d").date()
                    if linha.get("data")
                    else date.today()
                )
                dia = data_atual.day
                valor_parcela = valor_total / parcelas

                data_parcela = data_atual
                for i in range(parcelas):
                    data_parcela = (
                        data_parcela if i == 0 else proxima_data(data_parcela, dia)
                    )

                    if conta.tipo == TipoContaEnum.CREDITO and conta.dia_fechamento:
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
                    await repository.criar_transacao(ctx, transacao=nova_tx)
                    contagem_insercoes += 1

            except ValueError:
                typer.secho(
                    f"⚠️ Linha {contagem_linhas}: Erro de conversão de valores. Verifique 'valor', 'parcelas' ou 'conta_id'. Pulando.",
                    fg=typer.colors.YELLOW,
                )

    return contagem_linhas, contagem_insercoes
