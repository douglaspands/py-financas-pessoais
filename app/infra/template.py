from fastapi.templating import Jinja2Templates

from app.infra import utils

templates = Jinja2Templates(directory="templates")
templates.env.filters["formatar_moeda"] = utils.formatar_moeda
templates.env.filters["texto_capitalizado"] = utils.texto_capitalizado
