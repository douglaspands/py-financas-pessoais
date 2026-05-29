from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from app.account.enum import TipoContaEnum

if TYPE_CHECKING:
    from app.transaction.model import Transacao


class Conta(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    nome: str
    tipo: TipoContaEnum
    limite_ou_total: Optional[float] = Field(default=0.0)
    dia_fechamento: Optional[int] = Field(default=None)
    dia_vencimento: Optional[int] = Field(default=None)

    transacoes: List["Transacao"] = Relationship(back_populates="conta")

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
