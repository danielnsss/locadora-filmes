import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import delete, func, select

from banco.conexao import SessionLocal, engine
from banco.modelos_db import AluguelDB, Base, ClienteDB, FilmeDB
from banco.repositorios import RepositorioBanco


class TestConcorrenciaBanco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if engine.url.database != "locadora_testes":
            raise RuntimeError("Os testes só podem usar o banco locadora_testes.")

        Base.metadata.create_all(bind=engine)

    def setUp(self):
        self.filme_id = None
        self.cliente_ids = []

        with SessionLocal() as sessao:
            repositorio = RepositorioBanco(sessao)
            filme = repositorio.cadastrar_filme(
                "Filme para teste de concorrência",
                "Ficção científica",
                2014,
                "Registro temporário no banco de testes.",
                7.0,
                1,
            )
            primeiro_cliente = repositorio.cadastrar_cliente(
                "Cliente concorrente A", "89999990001"
            )
            segundo_cliente = repositorio.cadastrar_cliente(
                "Cliente concorrente B", "89999990002"
            )
            self.filme_id = filme.id
            self.cliente_ids = [primeiro_cliente.id, segundo_cliente.id]
            sessao.commit()

    def tearDown(self):
        if self.filme_id is None:
            return

        with SessionLocal() as sessao:
            sessao.execute(
                delete(AluguelDB).where(AluguelDB.filme_id == self.filme_id)
            )
            sessao.execute(
                delete(ClienteDB).where(ClienteDB.id.in_(self.cliente_ids))
            )
            sessao.execute(delete(FilmeDB).where(FilmeDB.id == self.filme_id))
            sessao.commit()

    def executar_em_paralelo(self, tarefas):
        barreira = threading.Barrier(2)

        def executar(tarefa):
            with SessionLocal() as sessao:
                repositorio = RepositorioBanco(sessao)
                barreira.wait(timeout=10)

                try:
                    tarefa(repositorio)
                    sessao.commit()
                    return "sucesso"
                except ValueError:
                    sessao.rollback()
                    return "rejeitado"

        with ThreadPoolExecutor(max_workers=2) as executor:
            futuros = [executor.submit(executar, tarefa) for tarefa in tarefas]
            return [futuro.result(timeout=20) for futuro in futuros]

    def test_01_dois_alugueis_simultaneos_do_ultimo_exemplar(self):
        tarefas = [
            lambda repositorio, cliente_id=cliente_id: repositorio.alugar_filme(
                self.filme_id, cliente_id, 1
            )
            for cliente_id in self.cliente_ids
        ]

        resultados = self.executar_em_paralelo(tarefas)
        self.assertCountEqual(resultados, ["sucesso", "rejeitado"])

        with SessionLocal() as sessao:
            quantidade = sessao.scalar(
                select(FilmeDB.quantidade_disponivel).where(
                    FilmeDB.id == self.filme_id
                )
            )
            total = sessao.scalar(
                select(func.count(AluguelDB.id)).where(
                    AluguelDB.filme_id == self.filme_id
                )
            )

        self.assertEqual(quantidade, 0)
        self.assertEqual(total, 1)

    def test_02_duas_devolucoes_simultaneas_do_mesmo_aluguel(self):
        with SessionLocal() as sessao:
            repositorio = RepositorioBanco(sessao)
            aluguel = repositorio.alugar_filme(
                self.filme_id, self.cliente_ids[0], 1
            )
            aluguel_id = aluguel.id
            sessao.commit()

        tarefas = [
            lambda repositorio: repositorio.devolver_filme(aluguel_id),
            lambda repositorio: repositorio.devolver_filme(aluguel_id),
        ]

        resultados = self.executar_em_paralelo(tarefas)
        self.assertCountEqual(resultados, ["sucesso", "rejeitado"])

        with SessionLocal() as sessao:
            quantidade = sessao.scalar(
                select(FilmeDB.quantidade_disponivel).where(
                    FilmeDB.id == self.filme_id
                )
            )
            aluguel = sessao.get(AluguelDB, aluguel_id)
            status = aluguel.status
            data_devolucao = aluguel.data_devolucao_real
            total = sessao.scalar(
                select(func.count(AluguelDB.id)).where(
                    AluguelDB.filme_id == self.filme_id
                )
            )

        self.assertEqual(quantidade, 1)
        self.assertEqual(status, "devolvido")
        self.assertIsNotNone(data_devolucao)
        self.assertEqual(total, 1)


if __name__ == "__main__":
    unittest.main()
