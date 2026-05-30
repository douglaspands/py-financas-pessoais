from datetime import date

from fastapi.templating import Jinja2Templates

from app.infra import utils
from app.transaction.enum import CategoriaTransacaoEnum

templates = Jinja2Templates(directory="templates")
templates.env.filters["formatar_moeda"] = utils.formatar_moeda
templates.env.filters["dia"] = lambda data: (
    str(data.day) if isinstance(data, date) else ""
)
templates.env.filters["quantidade"] = lambda lista: len(lista)
templates.env.globals["categorias_disponiveis"] = CategoriaTransacaoEnum  # type: ignore
