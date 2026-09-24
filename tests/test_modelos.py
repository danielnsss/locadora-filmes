
import unittest

from modelos.filme import Filme


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


if __name__ == "__main__":
    unittest.main()