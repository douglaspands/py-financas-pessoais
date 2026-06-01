from datetime import datetime, timezone
from typing import Any

from sqlmodel import delete, insert, select, update

from app.infra.context import Context
from app.transaction.model import Transacao


async def listar_transacoes(ctx: Context, **kwargs: Any) -> list[Transacao]:
    stmt = select(Transacao).filter_by(**kwargs)
    result = await ctx.session.exec(stmt)
    return list(result.all())


async def criar_transacao(ctx: Context, *, transacao: Transacao) -> int:
    transacao.created_at = transacao.updated_at = datetime.now(timezone.utc)
    stmt = insert(Transacao).values(**transacao.model_dump(exclude={"id"}))
    result = await ctx.session.exec(stmt)
    return result.lastrowid


async def obter_transacao(ctx: Context, *, pk: int) -> Transacao | None:
    stmt = select(Transacao).where(Transacao.id == pk)
    result = await ctx.session.exec(stmt)
    return result.first()


async def atualizar_transacao(ctx: Context, *, pk: int, **kwargs: Any) -> None:
    kwargs["updated_at"] = datetime.now(timezone.utc)
    stmt = update(Transacao).where(Transacao.id == pk).values(**kwargs)
    await ctx.session.exec(stmt)


async def excluir_transacao(ctx: Context, *, pk: int):
    stmt = delete(Transacao).where(Transacao.id == pk)
    await ctx.session.exec(stmt)


async def excluir_transacoes(ctx: Context, **kwargs: Any):
    stmt = delete(Transacao).filter_by(**kwargs)
    await ctx.session.exec(stmt)


async def limpar_transacoes(ctx: Context) -> None:
    stmt = delete(Transacao)
    await ctx.session.exec(stmt)
