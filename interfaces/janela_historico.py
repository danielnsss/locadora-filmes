from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

from interfaces.workers import CarregamentoThread

class JanelaHistorico(QDialog):
    devolucao_realizada = Signal()

    def __init__(self, locadora, parent=None):
        super().__init__(parent)

        self.locadora = locadora
        self.thread_historico = None
        self.setWindowTitle("Histórico de Locações")
        self.resize(1050, 540)
        self.criar_interface()
        self.atualizar_tabela()

    def criar_interface(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Histórico de locações")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        barra_filtros = QHBoxLayout()
        barra_filtros.addWidget(QLabel("Situação:"))

        self.filtro = QComboBox()
        self.filtro.addItem("Todos", None)
        self.filtro.addItem("Ativos", "ativo")
        self.filtro.addItem("Devolvidos", "devolvido")
        self.filtro.currentIndexChanged.connect(self.atualizar_tabela)
        barra_filtros.addWidget(self.filtro)
        barra_filtros.addStretch()

        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self.atualizar_tabela)
        barra_filtros.addWidget(botao_atualizar)
        layout.addLayout(barra_filtros)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels(["ID", "Filme", "Cliente", "Aluguel", "Prevista", "Devolução real", "Valor", "Situação"])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela.itemSelectionChanged.connect(self.atualizar_botao_devolver)
        layout.addWidget(self.tabela)

        self.label_resultado = QLabel()
        layout.addWidget(self.label_resultado)

        barra_botoes = QHBoxLayout()
        barra_botoes.addStretch()

        self.botao_devolver = QPushButton("Devolver selecionado")
        self.botao_devolver.setEnabled(False)
        self.botao_devolver.clicked.connect(self.confirmar_devolucao)
        barra_botoes.addWidget(self.botao_devolver)

        botao_fechar = QPushButton("Fechar")
        botao_fechar.clicked.connect(self.accept)
        barra_botoes.addWidget(botao_fechar)
        layout.addLayout(barra_botoes)

    def formatar_data(self, valor):
        if not valor:
            return "—"

        return date.fromisoformat(valor).strftime("%d/%m/%Y")

    def atualizar_tabela(self):
        if self.thread_historico is not None and self.thread_historico.isRunning():
            return

        status = self.filtro.currentData()
        thread = CarregamentoThread(lambda: self.carregar_historico(status), self)
        self.thread_historico = thread

        thread.concluido.connect(self.historico_carregado)
        thread.erro.connect(self.erro_carregamento_historico)
        thread.finished.connect(lambda: self.finalizar_thread_historico(thread))
        thread.finished.connect(thread.deleteLater)

        self.label_resultado.setText("Carregando histórico...")
        self.botao_devolver.setEnabled(False)
        thread.start()

    def carregar_historico(self, status):
        alugueis = self.locadora.listar_alugueis(status)
        filmes = {filme.id: filme.titulo for filme in self.locadora.listar_filmes()}
        clientes = {cliente.id: cliente.nome for cliente in self.locadora.listar_clientes()}

        return alugueis, filmes, clientes

    def historico_carregado(self, dados):
        alugueis, filmes, clientes = dados

        self.tabela.setRowCount(len(alugueis))

        for linha, aluguel in enumerate(alugueis):
            valores = [
                str(aluguel.id),
                filmes.get(aluguel.filme_id, f"Filme #{aluguel.filme_id} (não encontrado)"),
                clientes.get(aluguel.cliente_id, f"Cliente #{aluguel.cliente_id} (não encontrado)"),
                self.formatar_data(aluguel.data_aluguel),
                self.formatar_data(aluguel.data_devolucao_prevista),
                self.formatar_data(aluguel.data_devolucao_real),
                f"R$ {aluguel.valor_total:.2f}".replace(".", ","),
                "Ativo" if aluguel.status == "ativo" else "Devolvido"
            ]

            for coluna, valor in enumerate(valores):
                item = QTableWidgetItem(valor)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                if coluna == 0:
                    item.setData(Qt.ItemDataRole.UserRole, aluguel.id)

                if coluna == 7:
                    item.setData(Qt.ItemDataRole.UserRole, aluguel.status)

                self.tabela.setItem(linha, coluna, item)

        self.tabela.clearSelection()
        self.botao_devolver.setEnabled(False)
        self.label_resultado.setText(f"{len(alugueis)} aluguel(is) encontrado(s).")

    def erro_carregamento_historico(self, mensagem):
        self.tabela.setRowCount(0)
        self.label_resultado.setText("Não foi possível carregar o histórico.")
        self.botao_devolver.setEnabled(False)
        QMessageBox.warning(self, "Erro ao carregar histórico", mensagem)

    def finalizar_thread_historico(self, thread):
        if self.thread_historico is thread:
            self.thread_historico = None

    def atualizar_botao_devolver(self):
        linhas = self.tabela.selectionModel().selectedRows()
        linha = linhas[0].row() if linhas else -1
        item_status = self.tabela.item(linha, 7) if linha >= 0 else None
        self.botao_devolver.setEnabled(item_status is not None and item_status.data(Qt.ItemDataRole.UserRole) == "ativo")

    def confirmar_devolucao(self):
        linhas = self.tabela.selectionModel().selectedRows()
        linha = linhas[0].row() if linhas else -1
        item_id = self.tabela.item(linha, 0) if linha >= 0 else None
        item_status = self.tabela.item(linha, 7) if linha >= 0 else None

        if item_id is None or item_status is None or item_status.data(Qt.ItemDataRole.UserRole) != "ativo":
            QMessageBox.warning(self, "Seleção obrigatória", "Selecione um aluguel ativo para realizar a devolução.")
            return

        aluguel_id = item_id.data(Qt.ItemDataRole.UserRole)
        resposta = QMessageBox.question(self, "Confirmar devolução", f"Deseja devolver o filme do aluguel #{aluguel_id}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.locadora.devolver_filme(aluguel_id)

        except (OSError, ValueError, LookupError, RuntimeError) as erro:
            QMessageBox.warning(self, "Não foi possível devolver", str(erro))
            return

        self.devolucao_realizada.emit()
        self.atualizar_tabela()
        QMessageBox.information(self, "Devolução realizada", "Filme devolvido com sucesso.")

    def closeEvent(self, evento):
        if self.thread_historico is not None and self.thread_historico.isRunning():
            terminou = self.thread_historico.wait(2000)

            if not terminou:
                evento.ignore()
                return

        evento.accept()
