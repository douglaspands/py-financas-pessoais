from sqlmodel import select

from app.account.model import Conta
from app.infra.context import Context


def listar_contas(ctx: Context) -> list[Conta]:
    return list(ctx.session.exec(select(Conta)).all())


def obter_conta(ctx: Context, *, pk: int) -> Conta | None:
    conta = ctx.session.get(Conta, pk)
    return conta


def criar_conta(ctx: Context, *, conta: Conta) -> Conta:
    ctx.session.add(conta)
    return conta
