from sqlmodel import select

from app.infra.context import Context
from app.transaction.model import Transacao


def listar_transacoes(ctx: Context, *, mes_filtro: str) -> list[Transacao]:
    return list(
        ctx.session.exec(
            select(Transacao).where(Transacao.fatura_mes == mes_filtro)
        ).all()
    )


def criar_transacao(ctx: Context, *, transacao: Transacao) -> Transacao:
    ctx.session.add(transacao)
    return transacao


def limpar_transacoes(ctx: Context) -> None:
    ctx.session.query(Transacao).delete()
