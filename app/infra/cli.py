import typer

from app.account.command import app as account_typer
from app.transaction.command import app as transaction_typer


def create_app() -> typer.Typer:
    app = typer.Typer(help="CLI utilitária para o sistema de Controle Financeiro.")
    app.add_typer(transaction_typer)
    app.add_typer(account_typer)
    return app
