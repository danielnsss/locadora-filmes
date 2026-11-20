from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Literal

from pydantic import Field


class FilmeResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    genero: str
    ano: int
    sinopse: str
    preco_diaria: float
    quantidade_total: int
    quantidade_disponivel: int

class ClienteCriacao(BaseModel):
    nome: str
    telefone: str


class ClienteResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    telefone: str

class FilmeCriacao(BaseModel):
    titulo: str
    genero: str
    ano: int
    sinopse: str
    preco_diaria: float
    quantidade_total: int

class AluguelCriacao(BaseModel):
    filme_id: int = Field(strict=True, gt=0)
    cliente_id: int = Field(strict=True, gt=0)
    dias: int = Field(strict=True, gt=0)


class AluguelResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filme_id: int
    cliente_id: int
    data_aluguel: date
    data_devolucao_prevista: date
    data_devolucao_real: date | None
    valor_total: float
    status: Literal["ativo", "devolvido"]