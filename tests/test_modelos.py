
import unittest

from modelos.filme import Filme
from modelos.cliente import Cliente


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


if __name__ == "__main__":
    unittest.main()