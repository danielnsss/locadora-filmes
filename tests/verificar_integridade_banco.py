from banco.conexao import SessionLocal
from banco.repositorios import RepositorioBanco


def verificar_bloqueio(sessao, descricao, operacao):
    try:
        operacao()
    except ValueError as erro:
        sessao.rollback()
        print(f"OK - {descricao}: {erro}")
    else:
        sessao.rollback()
        raise AssertionError(f"Falha na protecao: {descricao}")


def main():
    with SessionLocal() as sessao:
        repositorio = RepositorioBanco(sessao)
        alugueis = repositorio.listar_alugueis("devolvido")

        if not alugueis:
            raise RuntimeError("Nenhum aluguel devolvido foi encontrado.")

        aluguel = alugueis[-1]
        filme_id = aluguel.filme_id
        cliente_id = aluguel.cliente_id
        aluguel_id = aluguel.id

        verificar_bloqueio(
            sessao,
            "Exclusao de filme com historico",
            lambda: repositorio.excluir_filme(filme_id)
        )

        verificar_bloqueio(
            sessao,
            "Exclusao de cliente com historico",
            lambda: repositorio.excluir_cliente(cliente_id)
        )

        verificar_bloqueio(
            sessao,
            "Segunda devolucao do mesmo aluguel",
            lambda: repositorio.devolver_filme(aluguel_id)
        )

        assert repositorio.obter_filme(filme_id) is not None
        assert repositorio.obter_cliente(cliente_id) is not None

        print("Todas as verificacoes de integridade passaram.")


if __name__ == "__main__":
    main()