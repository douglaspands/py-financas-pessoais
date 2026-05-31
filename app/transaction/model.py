from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from app.transaction.enum import CategoriaTransacaoEnum, TipoTransacaoEnum

if TYPE_CHECKING:
    from app.account.model import Conta


class Transacao(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    grupo_id: Optional[int] = Field(
        default=None, index=True
    )  # Para agrupar transações parceladas

    descricao: str
    valor: float
    data: date = Field(default_factory=date.today)
    paga: bool = Field(default=False)
    fatura_mes: Optional[str] = Field(default=None)

    categoria: CategoriaTransacaoEnum = Field(default=CategoriaTransacaoEnum.OUTROS)
    tipo: TipoTransacaoEnum = Field(default=TipoTransacaoEnum.UNICA)

    conta_id: int = Field(foreign_key="conta.id")
    conta: "Conta" = Relationship(back_populates="transacoes")

    # timestamp
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
        ),
    )
