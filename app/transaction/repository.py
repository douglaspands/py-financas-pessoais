from datetime import datetime, timezone

from sqlmodel import delete, insert, select

from app.infra.context import Context
from app.transaction.model import Transacao


async def listar_transacoes(ctx: Context, *, mes_filtro: str) -> list[Transacao]:
    stmt = select(Transacao).where(Transacao.fatura_mes == mes_filtro)
    result = await ctx.session.exec(stmt)
    return list(result.all())


async def criar_transacao(ctx: Context, *, transacao: Transacao) -> Transacao:
    transacao.created_at = transacao.updated_at = datetime.now(timezone.utc)
    stmt = insert(Transacao).values(**transacao.model_dump(exclude={"id"}))
    result = await ctx.session.exec(stmt)
    transacao.id = result.lastrowid
    return transacao


async def limpar_transacoes(ctx: Context) -> None:
    stmt = delete(Transacao)
    await ctx.session.exec(stmt)
