import os
import unittest
import threading
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from interfaces.janela_historico import JanelaHistorico


class LocadoraSimulada:
    def __init__(self):
        self.filmes = [SimpleNamespace(id=1, titulo="Interestelar")]
        self.clientes = [SimpleNamespace(id=1, nome="Maria")]
        self.alugueis = [
            SimpleNamespace(id=1, filme_id=1, cliente_id=1, data_aluguel="2026-09-22", data_devolucao_prevista="2026-09-25", data_devolucao_real=None, valor_total=15.0, status="ativo"),
            SimpleNamespace(id=2, filme_id=1, cliente_id=1, data_aluguel="2026-09-19", data_devolucao_prevista="2026-09-21", data_devolucao_real="2026-09-21", valor_total=10.0, status="devolvido")
        ]
        self.devolvidos = []
        self.erro_listagem = None
        self.erro_devolucao = None
        self.thread_id_historico = None

    def listar_filmes(self):
        return self.filmes

    def listar_clientes(self):
        return self.clientes

    def listar_alugueis(self, status=None):
        self.thread_id_historico = threading.get_ident()

        if self.erro_listagem:
            raise self.erro_listagem

        return [aluguel for aluguel in self.alugueis if status is None or aluguel.status == status]

    def devolver_filme(self, aluguel_id):
        if self.erro_devolucao:
            raise self.erro_devolucao

        aluguel = next(aluguel for aluguel in self.alugueis if aluguel.id == aluguel_id)

        if aluguel.status != "ativo":
            raise ValueError("Este aluguel já foi devolvido.")

        aluguel.status = "devolvido"
        aluguel.data_devolucao_real = date.today().isoformat()
        self.devolvidos.append(aluguel_id)
        return aluguel


class TestJanelaHistorico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.locadora = LocadoraSimulada()
        self.janela = JanelaHistorico(self.locadora)
        self.aguardar_historico()

    def aguardar_historico(self):
        thread = self.janela.thread_historico

        if thread is not None:
            terminou = thread.wait(2000)
            self.assertTrue(terminou, "A thread do histórico não terminou no tempo esperado.")

        self.app.processEvents()

    def tearDown(self):
        self.janela.close()
        self.app.processEvents()

    def test_01_carrega_historico_com_nomes(self):
        self.assertEqual(self.janela.tabela.rowCount(), 2)
        self.assertEqual(self.janela.tabela.item(0, 1).text(), "Interestelar")
        self.assertEqual(self.janela.tabela.item(0, 2).text(), "Maria")

    def test_02_filtra_ativos_e_devolvidos(self):
        self.janela.filtro.setCurrentIndex(1)
        self.aguardar_historico()

        self.assertEqual(self.janela.tabela.rowCount(), 1)
        self.assertEqual(self.janela.tabela.item(0, 7).text(), "Ativo")

        self.janela.filtro.setCurrentIndex(2)
        self.aguardar_historico()

        self.assertEqual(self.janela.tabela.rowCount(), 1)
        self.assertEqual(self.janela.tabela.item(0, 7).text(), "Devolvido")

    def test_03_so_habilita_devolucao_em_aluguel_ativo(self):
        self.assertFalse(self.janela.botao_devolver.isEnabled())
        self.janela.tabela.selectRow(0)
        self.assertTrue(self.janela.botao_devolver.isEnabled())
        self.janela.tabela.selectRow(1)
        self.assertFalse(self.janela.botao_devolver.isEnabled())

    def test_04_cancelamento_nao_modifica_aluguel(self):
        self.janela.tabela.selectRow(0)

        with patch("interfaces.janela_historico.QMessageBox.question", return_value=QMessageBox.StandardButton.No):
            self.janela.confirmar_devolucao()

        self.assertEqual(self.locadora.devolvidos, [])
        self.assertEqual(self.locadora.alugueis[0].status, "ativo")

    def test_05_devolucao_emite_sinal_e_atualiza_tabela(self):
        sinais = []
        self.janela.devolucao_realizada.connect(lambda: sinais.append(True))
        self.janela.tabela.selectRow(0)

        with patch("interfaces.janela_historico.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes):
            with patch("interfaces.janela_historico.QMessageBox.information"):
                self.janela.confirmar_devolucao()

        self.aguardar_historico()

        self.assertEqual(self.locadora.devolvidos, [1])
        self.assertEqual(sinais, [True])
        self.assertEqual(self.janela.tabela.item(0, 7).text(), "Devolvido")
        self.assertFalse(self.janela.botao_devolver.isEnabled())

    def test_06_falha_na_devolucao_exibe_aviso_sem_emitir_sinal(self):
        self.locadora.erro_devolucao = OSError("Falha simulada.")
        sinais = []
        self.janela.devolucao_realizada.connect(lambda: sinais.append(True))
        self.janela.tabela.selectRow(0)

        with patch("interfaces.janela_historico.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes):
            with patch("interfaces.janela_historico.QMessageBox.warning") as aviso:
                self.janela.confirmar_devolucao()

        aviso.assert_called_once()
        self.assertEqual(sinais, [])
        self.assertEqual(self.locadora.alugueis[0].status, "ativo")

    def test_07_falha_na_listagem_esvazia_tabela(self):
        self.locadora.erro_listagem = ValueError("Histórico inválido.")

        with patch("interfaces.janela_historico.QMessageBox.warning") as aviso:
            self.janela.atualizar_tabela()
            self.aguardar_historico()

            aviso.assert_called_once()

        self.assertEqual(self.janela.tabela.rowCount(), 0)
        self.assertFalse(self.janela.botao_devolver.isEnabled())

    def test_08_historico_e_carregado_em_thread_secundaria(self):
        self.assertIsNotNone(self.locadora.thread_id_historico)
        self.assertNotEqual(self.locadora.thread_id_historico, threading.get_ident())


if __name__ == "__main__":
    unittest.main()
