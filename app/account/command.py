import asyncio
import time
from typing import Annotated

import typer

from app.account import service
from app.account.enum import TipoContaEnum
from app.infra.context import get_context

app = typer.Typer(name="conta", help="Comandos relacionados a contas.")


@app.command("criar")
def criar_conta(
    nome: str = typer.Argument(..., help="Nome da conta a ser criada."),
    tipo: Annotated[
        TipoContaEnum,
        typer.Option(
            ...,
            "--tipo",
            "-t",
            help="Tipo da conta (ex: DEBITO, CREDITO).",
        ),
    ] = TipoContaEnum.CREDITO,
    limite: float = typer.Option(
        0.0, "--limite", "-l", help="Limite da conta (padrão: 0.0)."
    ),
    dia_fechamento: int = typer.Option(
        None, "--dia-fechamento", "-df", help="Dia de fechamento da conta (opcional)."
    ),
    dia_vencimento: int = typer.Option(
        None, "--dia-vencimento", "-dv", help="Dia de vencimento da conta (opcional)."
    ),
):
    async def main():
        async with get_context() as ctx:
            async with ctx.session.begin():
                conta_id = await service.cadastrar_conta(
                    ctx,
                    nome=nome,
                    tipo=tipo,
                    limite=limite,
                    dia_fechamento=dia_fechamento,
                    dia_vencimento=dia_vencimento,
                )
                typer.echo(f"Criando a conta: {nome}...")
        return conta_id

    try:
        start_time = time.perf_counter()
        conta_id = asyncio.run(main())
        end_time = time.perf_counter()
        typer.secho(
            f"⏱️ Tempo de execução: {end_time - start_time:.2f} segundos",
            fg=typer.colors.MAGENTA,
        )

    except Exception as e:
        typer.secho(
            f"❌ Ocorreu um erro durante a criação da conta '{nome}': {e}",
            fg=typer.colors.RED,
            bold=True,
        )
        raise typer.Exit(code=1)

    typer.secho(
        f"\n🚀 Sucesso! Conta '{nome}' ({conta_id}) criada com sucesso.",
        fg=typer.colors.GREEN,
        bold=True,
    )
