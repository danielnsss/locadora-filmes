
import json
import unittest

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from armazenamento.json_repository import JSONRepository


class TestJSONRepository(unittest.TestCase):

    def setUp(self):
        self.pasta_temporaria = TemporaryDirectory()
        self.addCleanup(self.pasta_temporaria.cleanup)
        self.repositorio = JSONRepository(self.pasta_temporaria.name)

    def test_criacao_arquivos(self):
        for tipo in ("filmes", "clientes", "alugueis"):
            caminho = Path(self.pasta_temporaria.name) / f"{tipo}.json"

            self.assertTrue(caminho.exists())
            self.assertEqual(self.repositorio.listar(tipo), [])

    def test_salvar_e_listar(self):
        registros = [{"id": 1, "titulo": "Interestelar", "genero": "Ficção científica"}]

        self.repositorio.salvar("filmes", registros)
        recuperados = self.repositorio.listar("filmes")

        self.assertEqual(recuperados, registros)

        caminho = Path(self.pasta_temporaria.name) / "filmes.json"
        conteudo = caminho.read_text(encoding="utf-8")

        self.assertIn("Ficção científica", conteudo)

    def test_proximo_id(self):
        self.assertEqual(self.repositorio.proximo_id("filmes"), 1)

        registros = [{"id": 1}, {"id": 4}, {"id": 2}]
        self.repositorio.salvar("filmes", registros)

        self.assertEqual(self.repositorio.proximo_id("filmes"), 5)

    def test_tipo_invalido(self):
        with self.assertRaises(ValueError):
            self.repositorio.listar("usuarios")

        with self.assertRaises(ValueError):
            self.repositorio.salvar("usuarios", [])

    def test_registros_invalidos(self):
        casos = [
            {"id": 1},
            [{"titulo": "Filme sem ID"}],
            [{"id": 1}, {"id": 1}],
            [{"id": -1}]
        ]

        for registros in casos:
            with self.subTest(registros=registros):
                with self.assertRaises(ValueError):
                    self.repositorio.salvar("filmes", registros)

    def test_json_corrompido(self):
        caminho = Path(self.pasta_temporaria.name) / "filmes.json"
        caminho.write_text("{invalido", encoding="utf-8")

        with self.assertRaises(json.JSONDecodeError):
            self.repositorio.listar("filmes")

        with self.assertRaises(json.JSONDecodeError):
            self.repositorio.salvar("filmes", [{"id": 1}])

        self.assertEqual(caminho.read_text(encoding="utf-8"), "{invalido")

    def test_estrutura_json_invalida(self):
        caminho = Path(self.pasta_temporaria.name) / "filmes.json"
        caminho.write_text('{"id": 1}', encoding="utf-8")

        with self.assertRaises(ValueError):
            self.repositorio.listar("filmes")

    def test_falha_gravacao_preserva_arquivo(self):
        registros_originais = [{"id": 1, "titulo": "Interestelar"}]
        self.repositorio.salvar("filmes", registros_originais)

        with patch("armazenamento.json_repository.os.replace", side_effect=OSError("Falha simulada")):
            with self.assertRaises(OSError):
                self.repositorio.salvar("filmes", [{"id": 2, "titulo": "Avatar"}])

        self.assertEqual(self.repositorio.listar("filmes"), registros_originais)

        temporarios = list(Path(self.pasta_temporaria.name).glob("*.tmp"))
        self.assertEqual(temporarios, [])


if __name__ == "__main__":
    unittest.main()