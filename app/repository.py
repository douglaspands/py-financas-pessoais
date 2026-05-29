from sqlmodel import select

from app.context import Context
from app.model import Conta, Transacao


def listar_contas(ctx: Context) -> list[Conta]:
    return list(ctx.session.exec(select(Conta)).all())


def obter_conta(ctx: Context, *, pk: int) -> Conta | None:
    conta = ctx.session.get(Conta, pk)
    return conta


def criar_conta(ctx: Context, *, conta: Conta) -> Conta:
    ctx.session.add(conta)
    return conta


def listar_transacoes(ctx: Context, *, mes_filtro: str) -> list[Transacao]:
    return list(
        ctx.session.exec(
            select(Transacao).where(Transacao.fatura_mes == mes_filtro)
        ).all()
    )


def limpar_transacoes(ctx: Context) -> None:
    ctx.session.query(Transacao).delete()
