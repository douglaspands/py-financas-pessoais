from datetime import date, datetime, timezone
from typing import List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from app.enum import CategoriaTransacao, TipoConta


class Conta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    tipo: TipoConta
    limite_ou_total: Optional[float] = Field(default=0.0)
    dia_fechamento: Optional[int] = Field(default=None)
    dia_vencimento: Optional[int] = Field(default=None)

    transacoes: List["Transacao"] = Relationship(back_populates="conta")

    # timestamp
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
        ),
    )


class Transacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    descricao: str
    valor: float
    data: date = Field(default_factory=date.today)
    paga: bool = Field(default=False)
    fatura_mes: Optional[str] = Field(default=None)

    # Novo campo de categoria
    categoria: CategoriaTransacao = Field(default=CategoriaTransacao.OUTROS)

    conta_id: int = Field(foreign_key="conta.id")
    conta: Conta = Relationship(back_populates="transacoes")

    # timestamp
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
        ),
    )
