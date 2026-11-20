from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dependencias import obter_sessao
from api.esquemas import ClienteCriacao, ClienteResposta
from banco.repositorios import RepositorioBanco


router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("", response_model=list[ClienteResposta])
def listar_clientes(sessao: Session = Depends(obter_sessao)):
    repositorio = RepositorioBanco(sessao)
    return repositorio.listar_clientes()


@router.get("/{cliente_id}", response_model=ClienteResposta)
def obter_cliente(
    cliente_id: int = Path(gt=0),
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)
    cliente = repositorio.obter_cliente(cliente_id)

    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    return cliente


@router.post("", response_model=ClienteResposta, status_code=201)
def cadastrar_cliente(
    dados: ClienteCriacao,
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)

    try:
        cliente = repositorio.cadastrar_cliente(**dados.model_dump())
        sessao.commit()
    except (ValueError, TypeError) as erro:
        sessao.rollback()
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    except IntegrityError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não foi possível cadastrar o cliente."
        ) from erro

    return cliente


@router.delete("/{cliente_id}", status_code=204)
def excluir_cliente(
    cliente_id: int = Path(gt=0),
    sessao: Session = Depends(obter_sessao)
):
    repositorio = RepositorioBanco(sessao)

    try:
        repositorio.excluir_cliente(cliente_id)
        sessao.commit()
    except LookupError as erro:
        sessao.rollback()
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ValueError as erro:
        sessao.rollback()
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    except IntegrityError as erro:
        sessao.rollback()
        raise HTTPException(
            status_code=409,
            detail="O cliente possui registros associados."
        ) from erro