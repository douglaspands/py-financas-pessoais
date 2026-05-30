# Financas Pessoais [EM DESENVOLVIMENTO]

Site para controlar gastos pessoais em python.

## Comandos

```sh
# Sincronizar dependencias
uv sync

# Executar as migrations
uv run alembic upgrade head

# Criar Conta
python main.py conta criar "Cartão Nubank" --tipo credito --dia-fechamento 3 --dia-vencimento 10

# Importar planilha csv de contas
python main.py transacao importar-csv ./var/fatura_202605.csv

# Executar servidor web
uv run uvicorn main:app --host "0.0.0.0" --port 8000

# Gerar scripts de migrations
uv run alembic revision --autogenerate -m "comentario sobre o script"

# Remover banco de dados
rm ./database/financeiro.db

# Remocao de todas as pastas __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +
```