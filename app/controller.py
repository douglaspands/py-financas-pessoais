from typing import Optional

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from app import service
from app.context import Context, get_context_from_request
from app.model import CategoriaTransacao, TipoConta

router = APIRouter()


@router.get("/")
def read_root(
    ctx: Context = Depends(get_context_from_request),
    mes_filtro: Optional[str] = None,
):
    transacoes = service.listar_transacoes(ctx, mes_filtro=mes_filtro)

    return ctx.template.TemplateResponse(
        request=ctx.request,
        name="index.html",
        context={
            "request": ctx.request,
            **transacoes,
        },
    )


@router.post("/nova-transacao")
def cadastrar_transacao(
    descricao: str = Form(...),
    valor: float = Form(...),
    conta_id: int = Form(...),
    categoria: CategoriaTransacao = Form(...),  # Recebe a categoria do form
    parcelas: int = Form(1),
    ctx: Context = Depends(get_context_from_request),
):
    with ctx.session.begin():
        fatura = service.cadastrar_transacao(
            ctx,
            descricao=descricao,
            valor=valor,
            conta_id=conta_id,
            categoria=categoria,
            parcelas=parcelas,
        )
    return RedirectResponse(url=f"/?mes_filtro={fatura}", status_code=303)


# Rota simples para cadastrar contas (mantida igual)
@router.post("/nova-conta")
def cadastrar_conta(
    nome: str = Form(...),
    tipo: TipoConta = Form(...),
    limite: float = Form(0.0),
    dia_fechamento: Optional[int] = Form(None),
    dia_vencimento: Optional[int] = Form(None),
    ctx: Context = Depends(get_context_from_request),
):
    with ctx.session.begin():
        service.cadastrar_conta(
            ctx,
            nome=nome,
            tipo=tipo,
            limite=limite,
            dia_fechamento=dia_fechamento,
            dia_vencimento=dia_vencimento,
        )
    return RedirectResponse(url="/", status_code=303)
