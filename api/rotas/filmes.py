from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dependencias import obter_sessao
from api.esquemas import FilmeCriacao, FilmeResposta
from banco.repositorios import RepositorioBanco


router = APIRouter(prefix="/filmes", tags=["Filmes"])


@router.get("", response_model=list[FilmeResposta])
def listar_filmes(
    termo: str | None = None,
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)

    if termo is not None:
        return repositorio.buscar_filmes(termo)

    return repositorio.listar_filmes()


@router.get("/{filme_id}", response_model=FilmeResposta)
def obter_filme(
    filme_id: int = Path(gt=0),
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)
    filme = repositorio.obter_filme(filme_id)

    if filme is None:
        raise HTTPException(
            status_code=404,
            detail="Filme não encontrado."
        )

    return filme


@router.post("", response_model=FilmeResposta, status_code=201)
def cadastrar_filme(
    dados: FilmeCriacao,
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)

    try:
        filme = repositorio.cadastrar_filme(**dados.model_dump())
        sessao.commit()

    except (ValueError, TypeError) as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=422,
            detail=str(erro)
        ) from erro

    except IntegrityError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não foi possível cadastrar o filme."
        ) from erro

    return filme


@router.delete("/{filme_id}", status_code=204)
def excluir_filme(
    filme_id: int = Path(gt=0),
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)

    try:
        repositorio.excluir_filme(filme_id)
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
            detail="O filme possui registros associados."
        ) from erro