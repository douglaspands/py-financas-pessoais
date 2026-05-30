from fastapi.templating import Jinja2Templates

from app.infra import utils
from app.transaction.enum import CategoriaTransacaoEnum

templates = Jinja2Templates(directory="templates")
templates.env.filters["formatar_moeda"] = utils.formatar_moeda
templates.env.globals["categorias_disponiveis"] = CategoriaTransacaoEnum
