import asyncio
import time
from pathlib import Path

import typer

from app.infra.context import get_context
from app.transaction import service

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
    async def main():
        async with get_context() as ctx:
            if limpar_banco:
                async with ctx.session.begin():
                    typer.echo("Limpando transações antigas...")
                    await service.limpar_transacoes(ctx)
                    typer.echo(f"Processando o arquivo: {arquivo.name}...")

            async with ctx.session.begin():
                (
                    contagem_linhas,
                    contagem_insercoes,
                ) = await service.importar_transacoes_csv(ctx, arquivo=arquivo)

            return contagem_linhas, contagem_insercoes

    if not arquivo.exists():
        typer.secho(
            f"Erro: O arquivo '{arquivo}' não foi encontrado.",
            fg=typer.colors.RED,
            bold=True,
        )
        raise typer.Exit(code=1)

    try:
        start_time = time.perf_counter()
        contagem_linhas, contagem_insercoes = asyncio.run(main())
        end_time = time.perf_counter()
        typer.secho(
            f"⏱️ Tempo de execução: {end_time - start_time:.2f} segundos",
            fg=typer.colors.MAGENTA,
        )

    except Exception as e:
        typer.secho(
            f"❌ Ocorreu um erro durante a importação: {e}",
            fg=typer.colors.RED,
            bold=True,
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
