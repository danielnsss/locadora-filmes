
import unittest

from modelos.filme import Filme
from modelos.cliente import Cliente
from modelos.aluguel import Aluguel

class TestFilme(unittest.TestCase):

    def test_criacao_filme(self):
        filme = Filme(1, "Interestelar", "Ficção científica", 2014, "Uma viagem pelo espaço.", 5.0, 3)

        self.assertEqual(filme.titulo, "Interestelar")
        self.assertEqual(filme.quantidade_disponivel, 3)

    def test_conversao_json(self):
        filme = Filme(1, "Interestelar", "Ficção científica", 2014, "Uma viagem pelo espaço.", 5.0, 3)

        dados = filme.to_dict()
        filme_recuperado = Filme.from_dict(dados)

        self.assertEqual(filme_recuperado.to_dict(), dados)

    def test_estoque_invalido(self):
        with self.assertRaises(ValueError):
            Filme(1, "Interestelar", "Ficção científica", 2014, "", 5.0, 3, quantidade_disponivel=4)


class TestCliente(unittest.TestCase):

    def test_criacao_cliente(self):
        cliente = Cliente(1, "Cliente Exemplo", "00000000000")

        self.assertEqual(cliente.id, 1)
        self.assertEqual(cliente.nome, "Cliente Exemplo")
        self.assertEqual(cliente.telefone, "00000000000")

    def test_conversao_json_cliente(self):
        cliente = Cliente(1, "Cliente Exemplo", "00000000000")

        dados = cliente.to_dict()
        cliente_recuperado = Cliente.from_dict(dados)

        self.assertEqual(cliente_recuperado.to_dict(), dados)

    def test_dados_invalidos_cliente(self):
        casos = [
            (0, "Cliente Exemplo", "00000000000"),
            (True, "Cliente Exemplo", "00000000000"),
            (1, " ", "00000000000"),
            (1, "Cliente Exemplo", " ")
        ]

        for id, nome, telefone in casos:
            with self.subTest(id=id, nome=nome, telefone=telefone):
                with self.assertRaises(ValueError):
                    Cliente(id, nome, telefone)

class TestAluguel(unittest.TestCase):

    def test_criacao_aluguel_ativo(self):
        aluguel = Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0)

        self.assertEqual(aluguel.id, 1)
        self.assertEqual(aluguel.filme_id, 1)
        self.assertEqual(aluguel.cliente_id, 1)
        self.assertEqual(aluguel.status, "ativo")
        self.assertIsNone(aluguel.data_devolucao_real)
        self.assertEqual(aluguel.valor_total, 15.0)

    def test_criacao_aluguel_devolvido(self):
        aluguel = Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0, status="devolvido", data_devolucao_real="2026-09-26")

        self.assertEqual(aluguel.status, "devolvido")
        self.assertEqual(aluguel.data_devolucao_real, "2026-09-26")

    def test_conversao_json_aluguel(self):
        aluguel = Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0)

        dados = aluguel.to_dict()
        aluguel_recuperado = Aluguel.from_dict(dados)

        self.assertEqual(aluguel_recuperado.to_dict(), dados)

    def test_status_invalido_aluguel(self):
        with self.assertRaises(ValueError):
            Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0, status="cancelado")

    def test_aluguel_ativo_com_data_devolucao(self):
        with self.assertRaises(ValueError):
            Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0, status="ativo", data_devolucao_real="2026-09-26")

    def test_aluguel_devolvido_sem_data(self):
        with self.assertRaises(ValueError):
            Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0, status="devolvido")

    def test_datas_invalidas_aluguel(self):
        casos = ["amanhã", "2026-99-99", "2026-02-30", "2025-02-29", "20260924", "2026-9-24"]

        for data_invalida in casos:
            with self.subTest(data=data_invalida):
                with self.assertRaises(ValueError):
                    Aluguel(1, 1, 1, data_invalida, "2026-09-27", 15.0)

    def test_data_prevista_invalida(self):
        for data_prevista in ("2026-02-30", "2026-09-24", "2026-09-23"):
            with self.subTest(data=data_prevista):
                with self.assertRaises(ValueError):
                    Aluguel(1, 1, 1, "2026-09-24", data_prevista, 15.0)

    def test_data_real_invalida(self):
        for data_real in ("2026-02-30", "2026-09-23", "amanhã"):
            with self.subTest(data=data_real):
                with self.assertRaises(ValueError):
                    Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0, status="devolvido", data_devolucao_real=data_real)

    def test_devolucao_antecipada_e_atrasada(self):
        for data_real in ("2026-09-24", "2026-09-26", "2026-09-29"):
            with self.subTest(data_real=data_real):
                aluguel = Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0, status="devolvido", data_devolucao_real=data_real)
                self.assertEqual(aluguel.data_devolucao_real, data_real)

    def test_data_bissexta_valida(self):
        aluguel = Aluguel(1, 1, 1, "2024-02-29", "2024-03-01", 5.0)
        self.assertEqual(aluguel.data_aluguel, "2024-02-29")

    def test_from_dict_rejeita_data_invalida(self):
        aluguel = Aluguel(1, 1, 1, "2026-09-24", "2026-09-27", 15.0)
        dados = {**aluguel.to_dict(), "data_aluguel": "2026-99-99"}
        with self.assertRaises(ValueError):
            Aluguel.from_dict(dados)


if __name__ == "__main__":
    unittest.main()