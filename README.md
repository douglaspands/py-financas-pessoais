# Financas Pessoais [EM DESENVOLVIMENTO]

Site para controlar gastos pessoais em python.

## Comandos

```sh
# Sincronizar dependencias
uv sync

# Executar servidor web
uv run uvicorn main:app --host "0.0.0.0" --port 8000

# Executar as migrations
uv run alembic upgrade head

# Gerar scripts de migrations
uv run alembic revision --autogenerate -m "comentario sobre o script"
```