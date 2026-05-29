from pathlib import Path

import typer

from app import service
from app.context import get_context

app = typer.Typer(name="importar", help="subcomando para importar transações.")


@app.command("csv")
def importar_csv(
    arquivo: Path = typer.Argument(
        ..., help="Caminho para o arquivo CSV de transações."
    ),
    limpar_banco: bool = typer.Option(
        False,
        "--limpar",
        "-l",
        help="Apaga todas as transações existentes antes da carga.",
    ),
):
    """
    Carrega transações em lote a partir de um arquivo CSV.
    """
    if not arquivo.exists():
        typer.secho(
            f"Erro: O arquivo '{arquivo}' não foi encontrado.",
            fg=typer.colors.RED,
            bold=True,
        )
        raise typer.Exit(code=1)

    with get_context() as ctx:
        # Opção para resetar a tabela de transações, se desejado
        if limpar_banco:
            with ctx.session.begin():
                typer.echo("Limpando transações antigas...")
                service.limpar_transacoes(ctx)
                typer.echo(f"Processando o arquivo: {arquivo.name}...")
        try:
            with ctx.session.begin():
                contagem_linhas, contagem_insercoes = service.importar_transacoes_csv(
                    ctx, arquivo=arquivo
                )

        except KeyError as e:
            typer.secho(
                f"❌ Erro de formatação na linha {contagem_linhas}: Coluna {e} ausente.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

        typer.secho(
            f"\n🚀 Sucesso! Processadas {contagem_linhas} linhas do CSV.",
            fg=typer.colors.GREEN,
            bold=True,
        )
        typer.secho(
            f"📦 {contagem_insercoes} registros de parcelas gerados no banco de dados.",
            fg=typer.colors.CYAN,
        )
