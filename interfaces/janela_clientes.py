from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox
)


class JanelaClientes(QDialog):
    def __init__(self, locadora, parent=None):
        super().__init__(parent)

        self.locadora = locadora
        self.clientes = []

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
        try:
            self.clientes = self.locadora.listar_clientes()

        except (OSError, ValueError) as erro:
            self.clientes = []
            QMessageBox.warning(self, "Erro", str(erro))

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
        linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.warning(self, "Seleção obrigatória", "Selecione um cliente para excluir.")
            return

        item_id = self.tabela.item(linha, 0)
        item_nome = self.tabela.item(linha, 1)

        if item_id is None or item_nome is None:
            QMessageBox.warning(self, "Erro", "Não foi possível identificar o cliente selecionado.")
            return

        cliente_id = item_id.data(Qt.ItemDataRole.UserRole)

        if cliente_id is None:
            QMessageBox.warning(self, "Erro", "O cliente selecionado não possui um identificador válido.")
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

        try:
            self.locadora.excluir_cliente(cliente_id)

        except (ValueError, LookupError, OSError) as erro:
            QMessageBox.warning(self, "Erro ao excluir cliente", str(erro))
            return

        self.atualizar_clientes()
        QMessageBox.information(self, "Cliente excluído", "Cliente excluído com sucesso.")