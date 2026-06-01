import csv
from datetime import date, datetime
from pathlib import Path

import typer
from dateutil.relativedelta import relativedelta

from app.account import service as account_service
from app.account.enum import TipoContaEnum
from app.infra import utils
from app.infra.context import Context
from app.transaction import repository
from app.transaction.enum import CategoriaTransacaoEnum, TipoTransacaoEnum
from app.transaction.model import Transacao


def calcular_fatura(data_compra: date, dia_fechamento: int) -> str:
    if data_compra.day < dia_fechamento:
        return data_compra.strftime("%Y-%m")
    else:
        return (data_compra + relativedelta(months=1)).strftime("%Y-%m")


async def listar_transacoes(ctx: Context, *, mes_filtro: str) -> dict:
    contas = await account_service.listar_contas(ctx)
    transacoes = await repository.listar_transacoes(ctx, fatura_mes=mes_filtro)
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
    tipo: TipoTransacaoEnum,
    quantidade_repeticoes: int,
    conta_id: int,
    categoria: CategoriaTransacaoEnum,
    data: date | None = None,
) -> str:
    conta = await account_service.obter_conta(ctx, pk=conta_id)
    if not conta:
        raise ValueError(f"Conta com ID {conta_id} não encontrada")

    data = data or date.today()
    valor_parcela = valor / quantidade_repeticoes

    grupo_id: int | None = None
    for i in range(quantidade_repeticoes):
        data_parcela = data + relativedelta(months=i)

        if conta.tipo == TipoContaEnum.CREDITO and conta.dia_fechamento:
            fatura = calcular_fatura(data_parcela, conta.dia_fechamento)
        else:
            fatura = data_parcela.strftime("%Y-%m")

        desc_final = (
            f"{descricao} ({i + 1}/{quantidade_repeticoes})"
            if quantidade_repeticoes > 1
            else descricao
        )

        nova_tx = Transacao(
            descricao=desc_final,
            valor=valor_parcela,
            data=data_parcela,
            fatura_mes=fatura,
            categoria=categoria,
            tipo=tipo,
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
    transacoes = [transacao]
    if transacao.tipo in (TipoTransacaoEnum.PARCELADA, TipoTransacaoEnum.RECORRENTE):
        trs = await repository.listar_transacoes(
            ctx, grupo_id=transacao.grupo_id or transacao.id
        )
        if transacao.tipo == TipoTransacaoEnum.RECORRENTE:
            for tx in sorted(trs, key=lambda tx: tx.id):
                if tx.id > transacao.id:
                    transacoes.append(tx)

    for tx in transacoes:
        await repository.excluir_transacao(ctx, pk=tx.id)


async def editar_transacao(
    ctx: Context,
    *,
    transacao_id: int,
    descricao: str,
    valor: float,
    categoria: CategoriaTransacaoEnum,
    conta_id: int,
    prox_recorrencias: bool,
):
    transacao = await repository.obter_transacao(ctx, pk=transacao_id)
    if not transacao:
        raise ValueError(f"Transação com ID {transacao_id} não encontrada")
    transacoes = [transacao]
    if prox_recorrencias:
        trs = await repository.listar_transacoes(
            ctx, grupo_id=transacao.grupo_id or transacao.id
        )
        for tx in sorted(trs, key=lambda tx: tx.id):
            if tx.id > transacao.id:
                transacoes.append(tx)
    for tx in transacoes:
        parcela_desc = f" ({tx.descricao.split('(')[-1]}" if "(" in tx.descricao else ""
        desc = "".join(descricao.split("(")[:-1]).strip()
        _pk = tx.id
        _descricao = desc + parcela_desc
        _valor = valor
        _categoria = categoria
        _conta_id = conta_id
        await repository.atualizar_transacao(
            ctx,
            pk=_pk,
            descricao=_descricao,
            valor=_valor,
            categoria=_categoria,
            conta_id=_conta_id,
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
                    tipo=TipoTransacaoEnum.PARCELADA
                    if parcelas > 1
                    else TipoTransacaoEnum.UNICA,
                    quantidade_repeticoes=parcelas,
                    data=data,
                )
                contagem_insercoes += parcelas

            except ValueError:
                typer.secho(
                    f"⚠️ Linha {contagem_linhas}: Erro de conversão de valores. Verifique 'valor', 'parcelas' ou 'conta_id'. Pulando.",
                    fg=typer.colors.YELLOW,
                )

    return contagem_linhas, contagem_insercoes
