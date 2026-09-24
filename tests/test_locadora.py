
import tempfile
import unittest

from datetime import date, timedelta
from unittest.mock import patch

from armazenamento.json_repository import JSONRepository
from servicos.locadora import Locadora


class TestLocadora(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.repositorio = JSONRepository(self.pasta.name)
        self.locadora = Locadora(self.repositorio)

        self.filme = self.locadora.cadastrar_filme("Interestelar", "Ficção científica", 2014, "Exploração espacial.", 5.0, 2)
        self.cliente = self.locadora.cadastrar_cliente("Maria Silva", "011999999999")

    def tearDown(self):
        self.pasta.cleanup()

    def test_01_aluguel_reduz_estoque_e_cria_registro(self):
        aluguel = self.locadora.alugar_filme(self.filme.id, self.cliente.id, 3)

        self.assertEqual(aluguel.status, "ativo")
        self.assertEqual(aluguel.filme_id, self.filme.id)
        self.assertEqual(aluguel.cliente_id, self.cliente.id)
        self.assertEqual(self.locadora.obter_filme(self.filme.id).quantidade_disponivel, 1)
        self.assertEqual(len(self.repositorio.listar("alugueis")), 1)

    def test_02_aluguel_calcula_valor_e_prazo(self):
        aluguel = self.locadora.alugar_filme(self.filme.id, self.cliente.id, 3)

        self.assertEqual(aluguel.valor_total, 15.0)
        self.assertEqual(date.fromisoformat(aluguel.data_devolucao_prevista) - date.fromisoformat(aluguel.data_aluguel), timedelta(days=3))
        self.assertIsNone(aluguel.data_devolucao_real)

    def test_03_nao_permite_alugar_filme_inexistente(self):
        with self.assertRaises(LookupError):
            self.locadora.alugar_filme(9999, self.cliente.id, 2)

        self.assertEqual(len(self.repositorio.listar("alugueis")), 0)

    def test_04_nao_permite_alugar_para_cliente_inexistente(self):
        with self.assertRaises(LookupError):
            self.locadora.alugar_filme(self.filme.id, 9999, 2)

        self.assertEqual(self.locadora.obter_filme(self.filme.id).quantidade_disponivel, 2)

    def test_05_nao_permite_alugar_sem_estoque(self):
        self.locadora.alugar_filme(self.filme.id, self.cliente.id, 1)
        self.locadora.alugar_filme(self.filme.id, self.cliente.id, 1)

        with self.assertRaises(ValueError):
            self.locadora.alugar_filme(self.filme.id, self.cliente.id, 1)

        self.assertEqual(self.locadora.obter_filme(self.filme.id).quantidade_disponivel, 0)
        self.assertEqual(len(self.locadora.listar_alugueis()), 2)

    def test_06_rejeita_quantidades_de_dias_invalidas(self):
        for dias in (0, -1, True, 1.5, "3"):
            with self.subTest(dias=dias):
                with self.assertRaises(ValueError):
                    self.locadora.alugar_filme(self.filme.id, self.cliente.id, dias)

        self.assertEqual(len(self.locadora.listar_alugueis()), 0)

    def test_07_lista_e_filtra_alugueis_por_status(self):
        primeiro = self.locadora.alugar_filme(self.filme.id, self.cliente.id, 2)
        segundo = self.locadora.alugar_filme(self.filme.id, self.cliente.id, 3)

        self.locadora.devolver_filme(primeiro.id)

        self.assertEqual(len(self.locadora.listar_alugueis()), 2)
        self.assertEqual([aluguel.id for aluguel in self.locadora.listar_alugueis("ativo")], [segundo.id])
        self.assertEqual([aluguel.id for aluguel in self.locadora.listar_alugueis("devolvido")], [primeiro.id])

        with self.assertRaises(ValueError):
            self.locadora.listar_alugueis("cancelado")

    def test_08_devolucao_restitui_estoque(self):
        aluguel = self.locadora.alugar_filme(self.filme.id, self.cliente.id, 2)

        devolvido = self.locadora.devolver_filme(aluguel.id)

        self.assertEqual(devolvido.status, "devolvido")
        self.assertEqual(devolvido.data_devolucao_real, date.today().isoformat())
        self.assertEqual(self.locadora.obter_filme(self.filme.id).quantidade_disponivel, 2)

    def test_09_nao_permite_devolver_duas_vezes(self):
        aluguel = self.locadora.alugar_filme(self.filme.id, self.cliente.id, 2)
        self.locadora.devolver_filme(aluguel.id)

        with self.assertRaises(ValueError):
            self.locadora.devolver_filme(aluguel.id)

        self.assertEqual(self.locadora.obter_filme(self.filme.id).quantidade_disponivel, 2)

    def test_10_nao_permite_devolver_aluguel_inexistente(self):
        with self.assertRaises(LookupError):
            self.locadora.devolver_filme(9999)

    def test_11_dados_persistem_ao_reabrir_repositorio(self):
        aluguel = self.locadora.alugar_filme(self.filme.id, self.cliente.id, 2)

        outro_repositorio = JSONRepository(self.pasta.name)
        outra_locadora = Locadora(outro_repositorio)

        self.assertEqual(outra_locadora.obter_filme(self.filme.id).quantidade_disponivel, 1)
        self.assertEqual(outra_locadora.listar_alugueis()[0].id, aluguel.id)

    def test_12_falha_no_estoque_reverte_aluguel(self):
        filmes_antes = self.repositorio.listar("filmes")
        alugueis_antes = self.repositorio.listar("alugueis")
        salvar_original = self.repositorio.salvar

        def salvar_com_falha(tipo, registros):
            if tipo == "filmes":
                raise OSError("Falha simulada ao gravar o estoque.")

            return salvar_original(tipo, registros)

        with patch.object(self.repositorio, "salvar", side_effect=salvar_com_falha):
            with self.assertRaises(RuntimeError):
                self.locadora.alugar_filme(self.filme.id, self.cliente.id, 2)

        self.assertEqual(self.repositorio.listar("filmes"), filmes_antes)
        self.assertEqual(self.repositorio.listar("alugueis"), alugueis_antes)

    def test_13_falha_no_estoque_reverte_devolucao(self):
        aluguel = self.locadora.alugar_filme(self.filme.id, self.cliente.id, 2)

        filmes_antes = self.repositorio.listar("filmes")
        alugueis_antes = self.repositorio.listar("alugueis")
        salvar_original = self.repositorio.salvar

        def salvar_com_falha(tipo, registros):
            if tipo == "filmes":
                raise OSError("Falha simulada ao gravar o estoque.")

            return salvar_original(tipo, registros)

        with patch.object(self.repositorio, "salvar", side_effect=salvar_com_falha):
            with self.assertRaises(RuntimeError):
                self.locadora.devolver_filme(aluguel.id)

        self.assertEqual(self.repositorio.listar("filmes"), filmes_antes)
        self.assertEqual(self.repositorio.listar("alugueis"), alugueis_antes)

    def test_14_falha_inicial_nao_modifica_estoque(self):
        filmes_antes = self.repositorio.listar("filmes")
        alugueis_antes = self.repositorio.listar("alugueis")

        def salvar_com_falha(tipo, registros):
            raise OSError("Falha simulada na primeira gravação.")

        with patch.object(self.repositorio, "salvar", side_effect=salvar_com_falha):
            with self.assertRaises(OSError):
                self.locadora.alugar_filme(self.filme.id, self.cliente.id, 2)

        self.assertEqual(self.repositorio.listar("filmes"), filmes_antes)
        self.assertEqual(self.repositorio.listar("alugueis"), alugueis_antes)


if __name__ == "__main__":
    unittest.main()
