from fastapi.templating import Jinja2Templates

from app.transaction.enum import CategoriaTransacaoEnum

templates = Jinja2Templates(directory="templates")
templates.env.globals["categorias_disponiveis"] = CategoriaTransacaoEnum
