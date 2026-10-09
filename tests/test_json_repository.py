import json
import unittest

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from armazenamento.json_repository import JSONRepository
from modelos.aluguel import Aluguel
from modelos.cliente import Cliente
from modelos.filme import Filme


class TestJSONRepository(unittest.TestCase):

    def setUp(self):
        self.pasta_temporaria = TemporaryDirectory()
        self.addCleanup(self.pasta_temporaria.cleanup)
        self.repositorio = JSONRepository(self.pasta_temporaria.name)

    def _filme(self, id=1, titulo="Interestelar"):
        return Filme(id, titulo, "Ficção científica", 2014, "Uma viagem pelo espaço.", 5.0, 3).to_dict()

    def _cliente(self, id=1):
        return Cliente(id, "Cliente Exemplo", "00000000000").to_dict()

    def _aluguel(self, id=1):
        return Aluguel(id, 1, 1, "2026-09-24", "2026-09-27", 15.0).to_dict()

    def test_criacao_arquivos(self):
        for tipo in ("filmes", "clientes", "alugueis"):
            caminho = Path(self.pasta_temporaria.name) / f"{tipo}.json"
            self.assertTrue(caminho.exists())
            self.assertEqual(self.repositorio.listar(tipo), [])

    def test_salvar_e_listar(self):
        registros = [self._filme()]
        self.repositorio.salvar("filmes", registros)
        recuperados = self.repositorio.listar("filmes")

        self.assertEqual(recuperados, registros)
        caminho = Path(self.pasta_temporaria.name) / "filmes.json"
        self.assertIn("Ficção científica", caminho.read_text(encoding="utf-8"))

    def test_proximo_id(self):
        self.assertEqual(self.repositorio.proximo_id("filmes"), 1)
        registros = [self._filme(1), self._filme(4), self._filme(2)]
        self.repositorio.salvar("filmes", registros)
        self.assertEqual(self.repositorio.proximo_id("filmes"), 5)

    def test_tipo_invalido(self):
        with self.assertRaises(ValueError):
            self.repositorio.listar("usuarios")
        with self.assertRaises(ValueError):
            self.repositorio.salvar("usuarios", [])
        with self.assertRaises(ValueError):
            self.repositorio.proximo_id("usuarios")

    def test_registros_invalidos(self):
        casos = [
            {"id": 1},
            [{"titulo": "Filme sem ID"}],
            [self._filme(1), self._filme(1)],
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
            self.repositorio.salvar("filmes", [self._filme()])

        self.assertEqual(caminho.read_text(encoding="utf-8"), "{invalido")

    def test_estrutura_json_invalida(self):
        caminho = Path(self.pasta_temporaria.name) / "filmes.json"
        caminho.write_text('{"id": 1}', encoding="utf-8")

        with self.assertRaises(ValueError):
            self.repositorio.listar("filmes")

    def test_falha_gravacao_preserva_arquivo(self):
        registros_originais = [self._filme()]
        self.repositorio.salvar("filmes", registros_originais)

        with patch("armazenamento.json_repository.os.replace", side_effect=OSError("Falha simulada")):
            with self.assertRaises(OSError):
                self.repositorio.salvar("filmes", [self._filme(2, "Avatar")])

        self.assertEqual(self.repositorio.listar("filmes"), registros_originais)
        temporarios = list(Path(self.pasta_temporaria.name).glob("*.tmp"))
        self.assertEqual(temporarios, [])

    def test_campos_ausentes_e_extras(self):
        for tipo, registro in (("filmes", self._filme()), ("clientes", self._cliente()), ("alugueis", self._aluguel())):
            faltando = registro.copy()
            faltando.pop(next(campo for campo in registro if campo != "id"))
            excedente = {**registro, "campo_inesperado": True}
            for dados in (faltando, excedente):
                with self.subTest(tipo=tipo, dados=dados):
                    with self.assertRaises(ValueError):
                        self.repositorio.salvar(tipo, [dados])

    def test_dados_invalidos_dos_modelos(self):
        filme = {**self._filme(), "quantidade_disponivel": 4}
        cliente = {**self._cliente(), "nome": " "}
        aluguel = {**self._aluguel(), "status": "cancelado"}

        for tipo, registro in (("filmes", filme), ("clientes", cliente), ("alugueis", aluguel)):
            with self.subTest(tipo=tipo):
                with self.assertRaises(ValueError):
                    self.repositorio.salvar(tipo, [registro])

    def test_dados_validos_nas_tres_colecoes(self):
        for tipo, registro in (("filmes", self._filme()), ("clientes", self._cliente()), ("alugueis", self._aluguel())):
            with self.subTest(tipo=tipo):
                self.repositorio.salvar(tipo, [registro])
                self.assertEqual(self.repositorio.listar(tipo), [registro])

    def test_listar_rejeita_registros_invalidos(self):
        for tipo, registro in (("filmes", self._filme()), ("clientes", self._cliente()), ("alugueis", self._aluguel())):
            incompleto = {"id": registro["id"]}
            caminho = Path(self.pasta_temporaria.name) / f"{tipo}.json"
            caminho.write_text(json.dumps([incompleto]), encoding="utf-8")
            with self.subTest(tipo=tipo):
                with self.assertRaises(ValueError):
                    self.repositorio.listar(tipo)

    def test_nao_sobrescrever_json_valido_mas_inconsistente(self):
        caminho = Path(self.pasta_temporaria.name) / "filmes.json"
        dados_incorretos = '[{"id": 1, "titulo": "Incompleto"}]'
        caminho.write_text(dados_incorretos, encoding="utf-8")

        with self.assertRaises(ValueError):
            self.repositorio.salvar("filmes", [self._filme()])

        self.assertEqual(caminho.read_text(encoding="utf-8"), dados_incorretos)

    def test_rejeita_data_invalida_em_alugueis(self):
        registro = {**self._aluguel(), "data_devolucao_prevista": "2026-02-30"}
        with self.assertRaises(ValueError):
            self.repositorio.salvar("alugueis", [registro])

    def test_proximo_id_rejeita_colecao_invalida(self):
        caminho = Path(self.pasta_temporaria.name) / "clientes.json"
        caminho.write_text('[{"id": 1}]', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.repositorio.proximo_id("clientes")

    def test_falha_serializacao_preserva_arquivo(self):
        originais = [self._filme()]
        self.repositorio.salvar("filmes", originais)

        with patch("armazenamento.json_repository.json.dump", side_effect=OSError("Falha simulada")):
            with self.assertRaises(OSError):
                self.repositorio.salvar("filmes", [self._filme(2)])

        self.assertEqual(self.repositorio.listar("filmes"), originais)
        self.assertEqual(list(Path(self.pasta_temporaria.name).glob("*.tmp")), [])

    def test_excluir_remove_registro(self):
        registros = [self._filme(1), self._filme(2, "Avatar")]
        self.repositorio.salvar("filmes", registros)

        self.repositorio.excluir("filmes", 1)

        self.assertEqual(self.repositorio.listar("filmes"), [registros[1]])

    def test_excluir_registro_inexistente(self):
        self.repositorio.salvar("filmes", [self._filme(1)])

        with self.assertRaises(LookupError):
            self.repositorio.excluir("filmes", 999)

        self.assertEqual(self.repositorio.listar("filmes"), [self._filme(1)])

    def test_excluir_rejeita_id_invalido(self):
        for registro_id in (0, -1, True, 1.5, "1"):
            with self.subTest(registro_id=registro_id):
                with self.assertRaises(ValueError):
                    self.repositorio.excluir("filmes", registro_id)

        with self.assertRaises(ValueError):
            self.repositorio.excluir("usuarios", 1)
if __name__ == "__main__":
    unittest.main()
