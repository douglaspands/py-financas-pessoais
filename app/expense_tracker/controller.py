from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.account import service as account_service
from app.account.enum import TipoContaEnum
from app.infra.context import Context, get_context_from_request
from app.transaction import service as transaction_service
from app.transaction.enum import CategoriaTransacaoEnum

router = APIRouter(tags=["gastos"], prefix="/gastos")


def mes_filtro_padrao() -> str:
    return date.today().strftime("%Y-%m")


@router.get("/", name="gastos:index", response_class=HTMLResponse)
async def index(
    ctx: Context = Depends(get_context_from_request),
    mes_filtro: Optional[str] = None,
) -> HTMLResponse:
    mes_filtro = mes_filtro or mes_filtro_padrao()
    transacoes = await transaction_service.listar_transacoes(ctx, mes_filtro=mes_filtro)
    return ctx.template.TemplateResponse(
        request=ctx.request,
        name="expense_tracker/index.html",
        context={
            "request": ctx.request,
            "mes_filtro": mes_filtro,
            **transacoes,
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/nova-transacao", name="gastos:cadastrar_transacao")
async def cadastrar_transacao(
    descricao: str = Form(...),
    valor: float = Form(...),
    conta_id: int = Form(...),
    categoria: CategoriaTransacaoEnum = Form(...),  # Recebe a categoria do form
    parcelas: int = Form(1),
    mes_filtro: Optional[str] = None,
    ctx: Context = Depends(get_context_from_request),
) -> RedirectResponse:
    mes_filtro = mes_filtro or mes_filtro_padrao()
    async with ctx.session.begin():
        await transaction_service.cadastrar_transacao(
            ctx,
            descricao=descricao,
            valor=valor,
            conta_id=conta_id,
            categoria=categoria,
            parcelas=parcelas,
        )
    return RedirectResponse(
        url=f"{ctx.request.url_for('gastos:index')!s}?mes_filtro={mes_filtro}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/deletar-transacao/{transacao_id}", name="gastos:deletar_transacao")
async def deletar_transacao(
    transacao_id: int,
    mes_filtro: Optional[str] = None,
    ctx: Context = Depends(get_context_from_request),
) -> RedirectResponse:
    mes_filtro = mes_filtro or mes_filtro_padrao()
    async with ctx.session.begin():
        await transaction_service.excluir_transacao(ctx, transacao_id=transacao_id)
    return RedirectResponse(
        url=f"{ctx.request.url_for('gastos:index')!s}?mes_filtro={mes_filtro}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/nova-conta", name="gastos:cadastrar_conta")
async def cadastrar_conta(
    nome: str = Form(...),
    tipo: TipoContaEnum = Form(...),
    limite: float = Form(0.0),
    dia_fechamento: Optional[int] = Form(None),
    dia_vencimento: Optional[int] = Form(None),
    mes_filtro: Optional[str] = None,
    ctx: Context = Depends(get_context_from_request),
) -> RedirectResponse:
    mes_filtro = mes_filtro or mes_filtro_padrao()
    async with ctx.session.begin():
        await account_service.cadastrar_conta(
            ctx,
            nome=nome,
            tipo=tipo,
            limite=limite,
            dia_fechamento=dia_fechamento,
            dia_vencimento=dia_vencimento,
        )
    mes_filtro = mes_filtro or mes_filtro_padrao()
    return RedirectResponse(
        url=f"{ctx.request.url_for('gastos:index')!s}?mes_filtro={mes_filtro}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
