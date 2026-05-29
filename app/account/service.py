from typing import Optional

from app.account import repository
from app.account.enum import TipoContaEnum
from app.account.model import Conta
from app.infra.context import Context


def cadastrar_conta(
    ctx: Context,
    *,
    nome: str,
    tipo: TipoContaEnum,
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


def listar_contas(ctx: Context) -> list[Conta]:
    return repository.listar_contas(ctx)


def obter_conta(ctx: Context, *, pk: int) -> Conta | None:
    return repository.obter_conta(ctx, pk=pk)
