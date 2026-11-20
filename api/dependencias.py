from banco.conexao import SessionLocal


def obter_sessao():
    with SessionLocal() as sessao:
        yield sessao