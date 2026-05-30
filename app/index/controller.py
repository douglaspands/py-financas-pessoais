from typing import Optional

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.account import service as account_service
from app.account.enum import TipoContaEnum
from app.infra.context import Context, get_context_from_request
from app.transaction import service as transaction_service
from app.transaction.enum import CategoriaTransacaoEnum

router = APIRouter()


@router.get("/")
async def index(
    ctx: Context = Depends(get_context_from_request),
    mes_filtro: Optional[str] = None,
) -> HTMLResponse:
    transacoes = await transaction_service.listar_transacoes(ctx, mes_filtro=mes_filtro)

    return ctx.template.TemplateResponse(
        request=ctx.request,
        name="index.html",
        context={
            "request": ctx.request,
            **transacoes,
        },
    )


@router.post("/nova-transacao")
async def cadastrar_transacao(
    descricao: str = Form(...),
    valor: float = Form(...),
    conta_id: int = Form(...),
    categoria: CategoriaTransacaoEnum = Form(...),  # Recebe a categoria do form
    parcelas: int = Form(1),
    ctx: Context = Depends(get_context_from_request),
) -> RedirectResponse:
    async with ctx.session.begin():
        # fatura = service.cadastrar_transacao(
        await transaction_service.cadastrar_transacao(
            ctx,
            descricao=descricao,
            valor=valor,
            conta_id=conta_id,
            categoria=categoria,
            parcelas=parcelas,
        )
    # return RedirectResponse(url=f"/?mes_filtro={fatura}", status_code=303)
    return RedirectResponse(url="/", status_code=303)


# Rota simples para cadastrar contas (mantida igual)
@router.post("/nova-conta")
async def cadastrar_conta(
    nome: str = Form(...),
    tipo: TipoContaEnum = Form(...),
    limite: float = Form(0.0),
    dia_fechamento: Optional[int] = Form(None),
    dia_vencimento: Optional[int] = Form(None),
    ctx: Context = Depends(get_context_from_request),
) -> RedirectResponse:
    async with ctx.session.begin():
        await account_service.cadastrar_conta(
            ctx,
            nome=nome,
            tipo=tipo,
            limite=limite,
            dia_fechamento=dia_fechamento,
            dia_vencimento=dia_vencimento,
        )
    return RedirectResponse(url="/", status_code=303)
