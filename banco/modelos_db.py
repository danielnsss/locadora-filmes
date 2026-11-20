from datetime import date

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class FilmeDB(Base):
    __tablename__ = "filmes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    genero: Mapped[str] = mapped_column(Text, nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    sinopse: Mapped[str] = mapped_column(Text, nullable=False)
    preco_diaria: Mapped[float] = mapped_column(Float, nullable=False)
    quantidade_total: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_disponivel: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("ano BETWEEN 1 AND 9999"),
        CheckConstraint("preco_diaria >= 0"),
        CheckConstraint("quantidade_total >= 0"),
        CheckConstraint("quantidade_disponivel BETWEEN 0 AND quantidade_total"),
    )


class ClienteDB(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    telefone: Mapped[str] = mapped_column(Text, nullable=False)


class AluguelDB(Base):
    __tablename__ = "alugueis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filme_id: Mapped[int] = mapped_column(
        ForeignKey("filmes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    data_aluguel: Mapped[date] = mapped_column(Date, nullable=False)
    data_devolucao_prevista: Mapped[date] = mapped_column(Date, nullable=False)
    data_devolucao_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="ativo")

    __table_args__ = (
        CheckConstraint("valor_total >= 0"),
        CheckConstraint("status IN ('ativo', 'devolvido')"),
        CheckConstraint("data_devolucao_prevista > data_aluguel"),
        CheckConstraint(
            "(status = 'ativo' AND data_devolucao_real IS NULL) OR "
            "(status = 'devolvido' AND data_devolucao_real IS NOT NULL)"
        ),
        CheckConstraint(
            "data_devolucao_real IS NULL OR data_devolucao_real >= data_aluguel"
        ),
    )