from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox

from interfaces.workers import CarregamentoThread


class JanelaClientes(QDialog):
    def __init__(self, locadora, parent=None):
        super().__init__(parent)

        self.locadora = locadora
        self.clientes = []
        self.thread_clientes = None

        self.thread_exclusao_cliente = None
        self.exclusao_cliente_ok = False
        self.exclusao_cliente_erro = None

        self.setWindowTitle("Clientes - Locadora de Filmes")
        self.resize(650, 450)

        self.criar_interface()
        self.atualizar_clientes()

    def criar_interface(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Clientes Cadastrados")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Telefone"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)

        layout.addWidget(self.tabela)

        botoes = QHBoxLayout()

        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self.atualizar_clientes)

        botao_excluir = QPushButton("Excluir cliente")
        botao_excluir.clicked.connect(self.excluir_cliente)

        botao_fechar = QPushButton("Fechar")
        botao_fechar.clicked.connect(self.close)

        botoes.addWidget(botao_atualizar)
        botoes.addWidget(botao_excluir)
        botoes.addStretch()
        botoes.addWidget(botao_fechar)

        layout.addLayout(botoes)

    def atualizar_clientes(self):
        if self.thread_clientes is not None and self.thread_clientes.isRunning():
            return

        thread = CarregamentoThread(self.locadora.listar_clientes, self)
        self.thread_clientes = thread

        thread.concluido.connect(self.clientes_carregados)
        thread.erro.connect(self.erro_carregamento_clientes)
        thread.finished.connect(lambda: self.finalizar_thread_clientes(thread))
        thread.finished.connect(thread.deleteLater)

        thread.start()

    def clientes_carregados(self, clientes):
        self.clientes = clientes
        self.preencher_tabela()

    def erro_carregamento_clientes(self, mensagem):
        self.clientes = []
        self.preencher_tabela()
        QMessageBox.warning(self, "Erro", mensagem)

    def finalizar_thread_clientes(self, thread):
        if self.thread_clientes is thread:
            self.thread_clientes = None

    def preencher_tabela(self):
        self.tabela.setRowCount(len(self.clientes))

        for linha, cliente in enumerate(self.clientes):
            item_id = QTableWidgetItem(str(cliente.id))
            item_nome = QTableWidgetItem(cliente.nome)
            item_telefone = QTableWidgetItem(cliente.telefone)

            item_id.setData(Qt.ItemDataRole.UserRole, cliente.id)

            self.tabela.setItem(linha, 0, item_id)
            self.tabela.setItem(linha, 1, item_nome)
            self.tabela.setItem(linha, 2, item_telefone)

    def excluir_cliente(self):
        if self.thread_exclusao_cliente is not None:
            return

        if self.thread_clientes is not None:
            return

        linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.warning(
                self,
                "Seleção obrigatória",
                "Selecione um cliente para excluir."
            )
            return

        item_id = self.tabela.item(linha, 0)
        item_nome = self.tabela.item(linha, 1)

        if item_id is None or item_nome is None:
            QMessageBox.warning(
                self,
                "Erro",
                "Não foi possível identificar o cliente selecionado."
            )
            return

        cliente_id = item_id.data(Qt.ItemDataRole.UserRole)

        if cliente_id is None:
            QMessageBox.warning(
                self,
                "Erro",
                "O cliente selecionado não possui um identificador válido."
            )
            return

        resposta = QMessageBox.question(
            self,
            "Excluir cliente",
            f'Deseja realmente excluir o cliente "{item_nome.text()}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        thread = CarregamentoThread(
            lambda: self.locadora.excluir_cliente(cliente_id),
            self
        )

        self.thread_exclusao_cliente = thread
        self.exclusao_cliente_ok = False
        self.exclusao_cliente_erro = None

        thread.concluido.connect(self.exclusao_cliente_concluida)
        thread.erro.connect(self.erro_exclusao_cliente)
        thread.finished.connect(self.finalizar_exclusao_cliente)
        thread.finished.connect(thread.deleteLater)

        self.setEnabled(False)
        thread.start()

    def exclusao_cliente_concluida(self, resultado):
        self.exclusao_cliente_ok = True


    def erro_exclusao_cliente(self, mensagem):
        self.exclusao_cliente_erro = mensagem


    def finalizar_exclusao_cliente(self):
        self.thread_exclusao_cliente = None
        self.setEnabled(True)

        if self.exclusao_cliente_ok:
            self.atualizar_clientes()

            QMessageBox.information(
                self,
                "Cliente excluído",
                "Cliente excluído com sucesso."
            )

        elif self.exclusao_cliente_erro is not None:
            QMessageBox.warning(
                self,
                "Erro ao excluir cliente",
                self.exclusao_cliente_erro
            )


    def closeEvent(self, evento):
        if self.thread_exclusao_cliente is not None or self.thread_clientes is not None:
            evento.ignore()
            return

        super().closeEvent(evento)

    def reject(self):
        if self.thread_exclusao_cliente is not None or self.thread_clientes is not None:
            return

        super().reject()