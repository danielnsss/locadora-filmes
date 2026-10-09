
import os
import unittest
import threading

from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox

from modelos.filme import Filme
from modelos.cliente import Cliente
from interfaces.janela_principal import JanelaPrincipal
from interfaces.janela_cadastro import JanelaCadastro
from interfaces.janela_clientes import JanelaClientes


class LocadoraSimulada:
    """Substitui temporariamente o serviço real nos testes da interface."""

    def __init__(self):
        self.filmes = [
            Filme(1, "Interestelar", "Ficção científica", 2014, "Viagem espacial.", 5.0, 3),
            Filme(2, "A Origem", "Ficção científica", 2010, "Um filme sobre sonhos.", 6.0, 2)
        ]
        self.clientes = []
        self.erro_filme = None
        self.erro_cliente = None
        self.erro_listagem = None

        self.erro_exclusao_filme = None
        self.erro_listagem_clientes = None
        self.erro_exclusao_cliente = None

        self.thread_id_listagem = None
        self.thread_id_clientes = None

    def listar_filmes(self):
        self.thread_id_listagem = threading.get_ident()

        if self.erro_listagem is not None:
            raise self.erro_listagem

        return list(self.filmes)

    def cadastrar_filme(self, titulo, genero, ano, sinopse, preco_diaria, quantidade_total):
        if self.erro_filme is not None:
            raise self.erro_filme

        novo_id = max((filme.id for filme in self.filmes), default=0) + 1
        filme = Filme(novo_id, titulo, genero, ano, sinopse, preco_diaria, quantidade_total)
        self.filmes.append(filme)

        return filme

    def cadastrar_cliente(self, nome, telefone):
        if self.erro_cliente is not None:
            raise self.erro_cliente

        novo_id = max((cliente.id for cliente in self.clientes), default=0) + 1
        cliente = Cliente(novo_id, nome, telefone)
        self.clientes.append(cliente)

        return cliente

    def listar_clientes(self):
        self.thread_id_clientes = threading.get_ident()

        if self.erro_listagem_clientes is not None:
            raise self.erro_listagem_clientes

        return list(self.clientes)

    def excluir_filme(self, filme_id):
        if self.erro_exclusao_filme is not None:
            raise self.erro_exclusao_filme

        for filme in self.filmes:
            if filme.id == filme_id:
                self.filmes.remove(filme)
                return filme

        raise LookupError("Filme não encontrado.")

    def excluir_cliente(self, cliente_id):
        if self.erro_exclusao_cliente is not None:
            raise self.erro_exclusao_cliente

        for cliente in self.clientes:
            if cliente.id == cliente_id:
                self.clientes.remove(cliente)
                return cliente

        raise LookupError("Cliente não encontrado.")


class TestInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.locadora = LocadoraSimulada()
        self.principal = JanelaPrincipal(self.locadora)
        self.principal.show()
        self.cadastro = None
        self.janela_clientes = None

        self.aguardar_catalogo()

    def tearDown(self):
        if self.cadastro is not None:
            self.cadastro.close()

        if self.janela_clientes is not None:
            self.janela_clientes.close()

        with patch("interfaces.janela_principal.QMessageBox.question", return_value=16384):
            self.principal.close()

        self.app.processEvents()

    def aguardar_catalogo(self):
        thread = self.principal.thread_catalogo

        if thread is not None:
            terminou = thread.wait(2000)
            self.assertTrue(terminou, "A thread do catálogo não terminou no tempo esperado.")

        self.app.processEvents()

    def aguardar_clientes(self):
        thread = self.janela_clientes.thread_clientes

        if thread is not None:
            terminou = thread.wait(2000)
            self.assertTrue(terminou, "A thread de clientes não terminou no tempo esperado.")

        self.app.processEvents()

    def criar_janela_cadastro(self):
        self.cadastro = JanelaCadastro(self.locadora, self.principal)
        return self.cadastro

    def clicar_botao(self, texto):
        botoes = self.cadastro.findChildren(QPushButton)
        botao = next((botao for botao in botoes if botao.text() == texto), None)

        self.assertIsNotNone(botao, f"Botão não encontrado: {texto}")
        botao.click()

    def preencher_filme(self):
        self.cadastro.campo_titulo.setText("Matrix")
        self.cadastro.campo_genero.setText("Ficção científica")
        self.cadastro.campo_ano.setValue(1999)
        self.cadastro.campo_sinopse.setPlainText("Um mundo simulado.")
        self.cadastro.campo_preco.setValue(7.50)
        self.cadastro.campo_quantidade.setValue(4)

    def test_01_catalogo_carregado_ao_iniciar(self):
        self.assertEqual(self.principal.tabela.rowCount(), 2)
        self.assertEqual(self.principal.tabela.item(0, 0).text(), "Interestelar")

    def test_02_pesquisa_filtra_os_filmes(self):
        self.principal.campo_pesquisa.setText("origem")

        self.assertEqual(self.principal.tabela.rowCount(), 1)
        self.assertEqual(self.principal.tabela.item(0, 0).text(), "A Origem")

        self.principal.campo_pesquisa.clear()
        self.assertEqual(self.principal.tabela.rowCount(), 2)

    def test_03_atualizar_catalogo_exibe_novo_filme(self):
        self.locadora.cadastrar_filme("Matrix", "Ficção científica", 1999, "Um mundo simulado.", 7.50, 4)

        self.principal.atualizar_catalogo()
        self.aguardar_catalogo()

        self.assertEqual(self.principal.tabela.rowCount(), 3)

    def test_04_botao_abre_janela_de_cadastro(self):
        with patch.object(JanelaCadastro, "exec", return_value=0) as executar:
            self.principal.acao_cadastrar.trigger()

        executar.assert_called_once()

    def test_05_filme_exige_campos_obrigatorios(self):
        self.criar_janela_cadastro()

        with patch("interfaces.janela_cadastro.QMessageBox.warning") as aviso:
            self.clicar_botao("Cadastrar filme")

        aviso.assert_called_once()
        self.assertEqual(len(self.locadora.filmes), 2)

    def test_06_cadastro_filme_emite_sinal_e_limpa_formulario(self):
        self.criar_janela_cadastro()
        self.preencher_filme()

        sinais = []
        self.cadastro.filme_cadastrado.connect(lambda: sinais.append("filme"))

        with patch("interfaces.janela_cadastro.QMessageBox.information") as mensagem:
            self.clicar_botao("Cadastrar filme")

        self.assertEqual(len(self.locadora.filmes), 3)
        self.assertEqual(self.locadora.filmes[-1].titulo, "Matrix")
        self.assertEqual(sinais, ["filme"])
        self.assertEqual(self.cadastro.campo_titulo.text(), "")
        mensagem.assert_called_once()

    def test_07_erro_no_servico_nao_emite_sinal_de_filme(self):
        self.criar_janela_cadastro()
        self.preencher_filme()
        self.locadora.erro_filme = ValueError("Cadastro de filme rejeitado.")

        sinais = []
        self.cadastro.filme_cadastrado.connect(lambda: sinais.append("filme"))

        with patch("interfaces.janela_cadastro.QMessageBox.warning") as aviso:
            self.clicar_botao("Cadastrar filme")

        self.assertEqual(len(self.locadora.filmes), 2)
        self.assertEqual(sinais, [])
        aviso.assert_called_once()

    def test_08_cliente_exige_campos_obrigatorios(self):
        self.criar_janela_cadastro()

        with patch("interfaces.janela_cadastro.QMessageBox.warning") as aviso:
            self.clicar_botao("Cadastrar cliente")

        aviso.assert_called_once()
        self.assertEqual(len(self.locadora.clientes), 0)

    def test_09_cadastro_cliente_preserva_telefone_e_emite_sinal(self):
        self.criar_janela_cadastro()
        self.cadastro.campo_nome.setText("Maria Silva")
        self.cadastro.campo_telefone.setText("011999999999")

        sinais = []
        self.cadastro.cliente_cadastrado.connect(lambda: sinais.append("cliente"))

        with patch("interfaces.janela_cadastro.QMessageBox.information") as mensagem:
            self.clicar_botao("Cadastrar cliente")

        self.assertEqual(len(self.locadora.clientes), 1)
        self.assertEqual(self.locadora.clientes[0].telefone, "011999999999")
        self.assertEqual(sinais, ["cliente"])
        self.assertEqual(self.cadastro.campo_nome.text(), "")
        mensagem.assert_called_once()

    def test_10_servico_indisponivel_exibe_aviso(self):
        self.criar_janela_cadastro()
        self.cadastro.campo_nome.setText("Maria Silva")
        self.cadastro.campo_telefone.setText("011999999999")
        self.locadora.erro_cliente = NotImplementedError("Serviço ainda não disponível.")

        sinais = []
        self.cadastro.cliente_cadastrado.connect(lambda: sinais.append("cliente"))

        with patch("interfaces.janela_cadastro.QMessageBox.warning") as aviso:
            self.clicar_botao("Cadastrar cliente")

        self.assertEqual(len(self.locadora.clientes), 0)
        self.assertEqual(sinais, [])
        aviso.assert_called_once()

    def test_11_sinal_de_cadastro_atualiza_catalogo_principal(self):
        self.criar_janela_cadastro()
        self.preencher_filme()
        self.cadastro.filme_cadastrado.connect(self.principal.atualizar_catalogo)

        with patch("interfaces.janela_cadastro.QMessageBox.information"):
            self.clicar_botao("Cadastrar filme")

        self.aguardar_catalogo()

        self.assertEqual(self.principal.tabela.rowCount(), 3)
        self.assertEqual(self.principal.tabela.item(2, 0).text(), "Matrix")

    def test_12_falha_na_listagem_exibe_mensagem_de_erro(self):
        self.locadora.erro_listagem = OSError("Falha na leitura dos filmes.")

        with patch("interfaces.janela_principal.QMessageBox.warning") as aviso:
            self.principal.atualizar_catalogo()
            self.aguardar_catalogo()

            aviso.assert_called_once()

        self.assertEqual(self.principal.tabela.rowCount(), 0)

    def test_13_excluir_filme_remove_do_catalogo(self):
        self.principal.tabela.selectRow(0)

        with patch("interfaces.janela_principal.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes):
            with patch("interfaces.janela_principal.QMessageBox.information") as mensagem:
                self.principal.excluir_filme()

        self.aguardar_catalogo()

        self.assertEqual(len(self.locadora.filmes), 1)
        self.assertEqual(self.locadora.filmes[0].titulo, "A Origem")
        self.assertEqual(self.principal.tabela.rowCount(), 1)
        mensagem.assert_called_once()

    def test_14_cancelar_exclusao_preserva_filme(self):
        self.principal.tabela.selectRow(0)

        with patch("interfaces.janela_principal.QMessageBox.question", return_value=QMessageBox.StandardButton.No):
            self.principal.excluir_filme()

        self.assertEqual(len(self.locadora.filmes), 2)
        self.assertEqual(self.principal.tabela.rowCount(), 2)

    def test_15_janela_clientes_carrega_clientes(self):
        self.locadora.cadastrar_cliente("Maria Silva", "011999999999")
        self.janela_clientes = JanelaClientes(self.locadora, self.principal)

        self.aguardar_clientes()

        self.assertEqual(self.janela_clientes.tabela.rowCount(), 1)
        self.assertEqual(self.janela_clientes.tabela.item(0, 1).text(), "Maria Silva")
        self.assertEqual(self.janela_clientes.tabela.item(0, 2).text(), "011999999999")

    def test_16_excluir_cliente_remove_da_tabela(self):
        self.locadora.cadastrar_cliente("Maria Silva", "011999999999")
        self.janela_clientes = JanelaClientes(self.locadora, self.principal)

        self.aguardar_clientes()
        self.janela_clientes.tabela.selectRow(0)

        with patch("interfaces.janela_clientes.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes):
            with patch("interfaces.janela_clientes.QMessageBox.information") as mensagem:
                self.janela_clientes.excluir_cliente()

        self.aguardar_clientes()

        self.assertEqual(self.locadora.clientes, [])
        self.assertEqual(self.janela_clientes.tabela.rowCount(), 0)
        mensagem.assert_called_once()

    def test_17_erro_na_exclusao_cliente_preserva_registro(self):
        self.locadora.cadastrar_cliente("Maria Silva", "011999999999")
        self.locadora.erro_exclusao_cliente = ValueError("Cliente possui aluguel registrado.")
        self.janela_clientes = JanelaClientes(self.locadora, self.principal)

        self.aguardar_clientes()
        self.janela_clientes.tabela.selectRow(0)

        with patch("interfaces.janela_clientes.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes):
            with patch("interfaces.janela_clientes.QMessageBox.warning") as aviso:
                self.janela_clientes.excluir_cliente()

        self.assertEqual(len(self.locadora.clientes), 1)
        self.assertEqual(self.janela_clientes.tabela.rowCount(), 1)
        aviso.assert_called_once()

    def test_18_acao_clientes_abre_janela(self):
        with patch("interfaces.janela_principal.JanelaClientes") as classe_janela:
            janela = classe_janela.return_value

            self.principal.acao_clientes.trigger()

            classe_janela.assert_called_once_with(self.locadora, self.principal)
            janela.exec.assert_called_once()

    def test_19_catalogo_e_carregado_em_thread_secundaria(self):
        self.assertIsNotNone(self.locadora.thread_id_listagem)
        self.assertNotEqual(self.locadora.thread_id_listagem, threading.get_ident())

    def test_20_falha_na_listagem_clientes_exibe_aviso(self):
        self.locadora.erro_listagem_clientes = OSError("Falha na leitura dos clientes.")

        with patch("interfaces.janela_clientes.QMessageBox.warning") as aviso:
            self.janela_clientes = JanelaClientes(self.locadora, self.principal)
            self.aguardar_clientes()

            aviso.assert_called_once()

        self.assertEqual(self.janela_clientes.tabela.rowCount(), 0)

    def test_21_clientes_sao_carregados_em_thread_secundaria(self):
        self.locadora.cadastrar_cliente("Maria Silva", "011999999999")
        self.janela_clientes = JanelaClientes(self.locadora, self.principal)

        self.aguardar_clientes()

        self.assertIsNotNone(self.locadora.thread_id_clientes)
        self.assertNotEqual(self.locadora.thread_id_clientes, threading.get_ident())

if __name__ == "__main__":
    unittest.main()