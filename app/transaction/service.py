import csv
from datetime import date, datetime, timedelta
from pathlib import Path

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
    ano = data.year + 1 if data.month == 12 else data.year
    mes = 1 if data.month == 12 else data.month + 1
    try:
        nova_data = date(ano, mes, dia)
    except BaseException:
        ano = ano + 1 if mes == 12 else ano
        mes = 1 if mes == 12 else mes + 1
        dia = 1
        nova_data = (date(ano, mes, dia)) - timedelta(days=1)
    return nova_data


async def listar_transacoes(ctx: Context, *, mes_filtro: str) -> dict:
    contas = await account_service.listar_contas(ctx)
    transacoes = await repository.listar_transacoes(ctx, mes_filtro=mes_filtro)
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
        "transacoes": sorted(
            transacoes, key=lambda tx: f"{tx.data}_{tx.created_at}", reverse=True
        ),
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
    data: date | None = None,
) -> str:
    conta = await account_service.obter_conta(ctx, pk=conta_id)
    if not conta:
        raise ValueError(f"Conta com ID {conta_id} não encontrada")

    data = data or date.today()
    dia = data.day
    valor_parcela = valor / parcelas

    data_parcela = data
    grupo_id: int | None = None
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
            data=data,
            fatura_mes=fatura,
            categoria=categoria,
            conta_id=conta_id,
            grupo_id=grupo_id,
        )
        nova_tx.id = await repository.criar_transacao(ctx, transacao=nova_tx)
        if not grupo_id:
            grupo_id = nova_tx.id
    return fatura


async def excluir_transacao(ctx: Context, *, transacao_id: int):
    transacao = await repository.obter_transacao(ctx, pk=transacao_id)
    if not transacao:
        raise ValueError(f"Transação com ID {transacao_id} não encontrada")
    await repository.excluir_transacao(ctx, pk=transacao.id)
    await repository.excluir_grupo_transacoes(
        ctx, grupo_id=transacao.grupo_id or transacao.id
    )


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
                conta_id = int(linha["conta_id"])
                categoria_str = utils.remover_acentos(
                    linha.get("categoria", "outros").lower()
                )
                categoria = CategoriaTransacaoEnum(categoria_str)
                parcelas = int(linha.get("parcelas", 1))
                data: date = (
                    datetime.strptime(linha["data"], r"%Y-%m-%d").date()
                    if linha.get("data")
                    else date.today()
                )
                await cadastrar_transacao(
                    ctx,
                    descricao=descricao,
                    valor=valor_total,
                    conta_id=conta_id,
                    categoria=categoria,
                    parcelas=parcelas,
                    data=data,
                )
                contagem_insercoes += parcelas

            except ValueError:
                typer.secho(
                    f"⚠️ Linha {contagem_linhas}: Erro de conversão de valores. Verifique 'valor', 'parcelas' ou 'conta_id'. Pulando.",
                    fg=typer.colors.YELLOW,
                )

    return contagem_linhas, contagem_insercoes
