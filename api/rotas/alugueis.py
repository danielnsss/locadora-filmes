from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dependencias import obter_sessao
from api.esquemas import AluguelCriacao, AluguelResposta
from banco.repositorios import RepositorioBanco


router = APIRouter(prefix="/alugueis", tags=["Aluguéis"])


@router.get("", response_model=list[AluguelResposta])
def listar_alugueis(
    status: Literal["ativo", "devolvido"] | None = None,
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)
    return repositorio.listar_alugueis(status)


@router.post("", response_model=AluguelResposta, status_code=201)
def alugar_filme(
    dados: AluguelCriacao,
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)

    try:
        aluguel = repositorio.alugar_filme(**dados.model_dump())
        sessao.commit()

    except LookupError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        ) from erro

    except ValueError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=409,
            detail=str(erro)
        ) from erro

    except IntegrityError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não foi possível registrar o aluguel."
        ) from erro

    return aluguel


@router.patch("/{aluguel_id}/devolucao", response_model=AluguelResposta)
def devolver_filme(
    aluguel_id: int = Path(gt=0),
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)

    try:
        aluguel = repositorio.devolver_filme(aluguel_id)
        sessao.commit()

    except LookupError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        ) from erro

    except ValueError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=409,
            detail=str(erro)
        ) from erro

    except IntegrityError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não foi possível registrar a devolução."
        ) from erro

    return aluguel