import unittest

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from banco.conexao import engine
from banco.modelos_db import AluguelDB, Base, FilmeDB
from banco.repositorios import RepositorioBanco


class TestTransacoesBanco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if engine.url.database != "locadora_testes":
            raise RuntimeError("Os testes so podem usar o banco locadora_testes.")

        Base.metadata.create_all(bind=engine)

    def setUp(self):
        self.conexao = engine.connect()
        self.transacao = self.conexao.begin()
        self.sessao = Session(
            bind=self.conexao,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        self.repositorio = RepositorioBanco(self.sessao)

    def tearDown(self):
        self.sessao.close()
        self.transacao.rollback()
        self.conexao.close()

    def criar_cenario(self, quantidade=3):
        filme = self.repositorio.cadastrar_filme(
            "Filme de teste de transacao",
            "Ficcao cientifica",
            2014,
            "Registro exclusivo do banco de testes.",
            7.0,
            quantidade,
        )
        cliente = self.repositorio.cadastrar_cliente(
            "Cliente de teste de transacao",
            "89999990001",
        )
        self.sessao.commit()
        return filme.id, cliente.id

    def consultar_estoque(self, filme_id):
        consulta = select(FilmeDB.quantidade_disponivel).where(FilmeDB.id == filme_id)
        return self.conexao.execute(consulta).scalar_one()

    def contar_alugueis(self, filme_id):
        consulta = select(func.count(AluguelDB.id)).where(AluguelDB.filme_id == filme_id)
        return self.conexao.execute(consulta).scalar_one()

    def test_01_rollback_do_aluguel_restaura_estoque(self):
        filme_id, cliente_id = self.criar_cenario()

        self.repositorio.alugar_filme(filme_id, cliente_id, 3)
        self.sessao.rollback()

        self.assertEqual(self.consultar_estoque(filme_id), 3)
        self.assertEqual(self.contar_alugueis(filme_id), 0)

    def test_02_rollback_da_devolucao_preserva_aluguel_ativo(self):
        filme_id, cliente_id = self.criar_cenario()

        aluguel = self.repositorio.alugar_filme(filme_id, cliente_id, 3)
        aluguel_id = aluguel.id
        self.sessao.commit()

        self.repositorio.devolver_filme(aluguel_id)
        self.sessao.rollback()

        consulta = select(AluguelDB.status, AluguelDB.data_devolucao_real).where(
            AluguelDB.id == aluguel_id
        )
        status, data_devolucao = self.conexao.execute(consulta).one()

        self.assertEqual(status, "ativo")
        self.assertIsNone(data_devolucao)
        self.assertEqual(self.consultar_estoque(filme_id), 2)

    def test_03_estoque_esgotado_nao_gera_segundo_aluguel(self):
        filme_id, cliente_id = self.criar_cenario(quantidade=1)

        self.repositorio.alugar_filme(filme_id, cliente_id, 1)
        self.sessao.commit()

        with self.assertRaisesRegex(ValueError, "Não há exemplares disponíveis"):
            self.repositorio.alugar_filme(filme_id, cliente_id, 1)

        self.sessao.rollback()
        self.assertEqual(self.consultar_estoque(filme_id), 0)
        self.assertEqual(self.contar_alugueis(filme_id), 1)


if __name__ == "__main__":
    unittest.main()
