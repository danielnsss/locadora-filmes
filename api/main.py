from contextlib import asynccontextmanager
from api.rotas.filmes import router as roteador_filmes
from api.rotas.clientes import router as roteador_clientes
from api.rotas.alugueis import router as roteador_alugueis

from fastapi import FastAPI
from sqlalchemy import text

from banco.conexao import engine
from banco.modelos_db import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Locadora de Filmes",
    lifespan=lifespan,
)

app.include_router(roteador_alugueis)
app.include_router(roteador_clientes)
app.include_router(roteador_filmes)

@app.get("/saude")
def verificar_saude():
    with engine.connect() as conexao:
        conexao.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "banco": "conectado",
    }