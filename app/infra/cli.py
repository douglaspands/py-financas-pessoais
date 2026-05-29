import typer

from app.transaction import command


def create_app() -> typer.Typer:
    app = typer.Typer(help="CLI utilitária para o sistema de Controle Financeiro.")
    app.add_typer(command.app)
    return app
