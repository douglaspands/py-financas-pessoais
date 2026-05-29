from datetime import date, timedelta
from typing import Optional

from app import respository
from app.context import Context
from app.enum import CategoriaTransacao
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
    contas = respository.listar_contas(ctx)
    if not mes_filtro:
        mes_filtro = date.today().strftime("%Y-%m")

    transacoes = respository.listar_transacoes(ctx, mes_filtro=mes_filtro)

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
    conta = respository.obter_conta(ctx, pk=conta_id)
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
        ctx.session.add(nova_tx)

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
    respository.criar_conta(ctx, conta=nova_conta)
