import csv
from datetime import date, timedelta
from pathlib import Path

import typer

# Importando os elementos do seu projeto atual
from database import engine
from sqlmodel import Session

from app.model import CategoriaTransacao, Conta, TipoConta, Transacao
from app.service import calcular_fatura  # Reaproveitando sua função de lógica de data

# Inicializa o app do Typer
app = typer.Typer(help="CLI utilitária para o sistema de Controle Financeiro.")


@app.command()
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

    with Session(engine) as session:
        # Opção para resetar a tabela de transações, se desejado
        if limpar_banco:
            typer.echo("Limpando transações antigas...")
            session.query(Transacao).delete()
            session.commit()

        typer.echo(f"Processando o arquivo: {arquivo.name}...")

        contagem_linhas = 0
        contagem_insercoes = 0

        with open(arquivo, mode="r", encoding="utf-8") as f:
            leitor = csv.DictReader(f)

            for linha in leitor:
                contagem_linhas += 1
                try:
                    # Parse e validação dos dados do CSV
                    descricao = linha["descricao"]
                    valor_total = float(linha["valor"])
                    parcelas = int(linha.get("parcelas", 1))
                    categoria_str = linha.get("categoria", "outros").lower()
                    conta_id = int(linha["conta_id"])

                    # Valida a categoria com o Enum
                    categoria = CategoriaTransacao(categoria_str)

                    # Busca a conta para aplicar a regra de fechamento de fatura
                    conta = session.get(Conta, conta_id)
                    if not conta:
                        typer.secho(
                            f"⚠️ Linha {contagem_linhas}: Conta ID {conta_id} não encontrada. Pulando.",
                            fg=typer.colors.YELLOW,
                        )
                        continue

                    data_atual = date.today()
                    valor_parcela = valor_total / parcelas

                    # Aplica a mesma lógica de parcelamento do seu main.py
                    for i in range(parcelas):
                        data_parcela = data_atual + timedelta(days=30 * i)

                        if conta.tipo == TipoConta.CREDITO and conta.dia_fechamento:
                            fatura = calcular_fatura(data_parcela, conta.dia_fechamento)
                        else:
                            fatura = data_parcela.strftime("%Y-%m")

                        desc_final = (
                            f"{descricao} ({i + 1}/{parcelas})"
                            if parcelas > 1
                            else descricao
                        )

                        nova_tx = Transacao(
                            descricao=desc_final,
                            valor=valor_parcela,
                            data=data_atual,
                            fatura_mes=fatura,
                            categoria=categoria,
                            conta_id=conta_id,
                        )
                        session.add(nova_tx)
                        contagem_insercoes += 1

                except KeyError as e:
                    typer.secho(
                        f"❌ Erro de formatação na linha {contagem_linhas}: Coluna {e} ausente.",
                        fg=typer.colors.RED,
                    )
                    raise typer.Exit(code=1)
                except ValueError:
                    typer.secho(
                        f"⚠️ Linha {contagem_linhas}: Erro de conversão de valores. Verifique 'valor', 'parcelas' ou 'conta_id'. Pulando.",
                        fg=typer.colors.YELLOW,
                    )
                    continue

        # Commita todas as transações processadas com sucesso
        session.commit()

        typer.secho(
            f"\n🚀 Sucesso! Processadas {contagem_linhas} linhas do CSV.",
            fg=typer.colors.GREEN,
            bold=True,
        )
        typer.secho(
            f"📦 {contagem_insercoes} registros de parcelas gerados no banco de dados.",
            fg=typer.colors.CYAN,
        )
