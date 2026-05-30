from datetime import datetime, timezone

from sqlmodel import insert, select

from app.account.model import Conta
from app.infra.context import Context


async def listar_contas(ctx: Context) -> list[Conta]:
    stmt = select(Conta)
    result = await ctx.session.exec(stmt)
    return list(result.all())


async def obter_conta(ctx: Context, *, pk: int) -> Conta | None:
    stmt = select(Conta).where(Conta.id == pk)
    result = await ctx.session.exec(stmt)
    return result.first()


async def criar_conta(ctx: Context, *, conta: Conta) -> Conta:
    conta.created_at = conta.updated_at = datetime.now(timezone.utc)
    stmt = insert(Conta).values(**conta.model_dump(exclude={"id"}))
    result = await ctx.session.exec(stmt)
    conta.id = result.lastrowid
    return conta
