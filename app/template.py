from fastapi.templating import Jinja2Templates

from app.model import CategoriaTransacao

templates = Jinja2Templates(directory="templates")
templates.env.globals["categorias_disponiveis"] = CategoriaTransacao
