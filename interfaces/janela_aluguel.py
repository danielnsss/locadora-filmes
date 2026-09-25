
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout
)


class JanelaAluguel(QDialog):
    aluguel_realizado = Signal()

    def __init__(self, locadora, filme_id, parent=None):
        super().__init__(parent)

        self.locadora = locadora
        self.filme = self.locadora.obter_filme(filme_id)
        self.clientes = self.locadora.listar_clientes()

        self.setWindowTitle("Aluguel de Filme")
        self.setMinimumWidth(450)

        self.criar_interface()
        self.atualizar_valor()

    def criar_interface(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Alugar Filme")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        formulario = QFormLayout()

        self.label_filme = QLabel(self.filme.titulo)
        self.label_genero = QLabel(self.filme.genero)
        self.label_preco = QLabel(self.formatar_moeda(self.filme.preco_diaria))
        self.label_disponibilidade = QLabel(str(self.filme.quantidade_disponivel))

        formulario.addRow("Filme:", self.label_filme)
        formulario.addRow("Gênero:", self.label_genero)
        formulario.addRow("Preço da diária:", self.label_preco)
        formulario.addRow("Disponíveis:", self.label_disponibilidade)

        self.combo_clientes = QComboBox()
        self.combo_clientes.setMinimumWidth(250)

        for cliente in self.clientes:
            self.combo_clientes.addItem(f"{cliente.nome} — {cliente.telefone}", cliente.id)

        formulario.addRow("Cliente:", self.combo_clientes)

        self.campo_dias = QSpinBox()
        self.campo_dias.setRange(1, 365)
        self.campo_dias.setValue(1)
        self.campo_dias.setSuffix(" dia(s)")
        self.campo_dias.valueChanged.connect(self.atualizar_valor)

        formulario.addRow("Período:", self.campo_dias)

        self.label_valor = QLabel()
        self.label_valor.setStyleSheet("font-size: 18px; font-weight: bold; color: #15803d;")
        formulario.addRow("Valor total:", self.label_valor)

        layout.addLayout(formulario)

        if not self.clientes:
            aviso = QLabel("Nenhum cliente cadastrado. Cadastre um cliente antes de realizar o aluguel.")
            aviso.setWordWrap(True)
            layout.addWidget(aviso)

        if self.filme.quantidade_disponivel == 0:
            aviso = QLabel("Este filme não possui exemplares disponíveis.")
            aviso.setWordWrap(True)
            layout.addWidget(aviso)

        botoes = QHBoxLayout()

        self.botao_confirmar = QPushButton("Confirmar aluguel")
        self.botao_confirmar.setEnabled(bool(self.clientes) and self.filme.quantidade_disponivel > 0)
        self.botao_confirmar.clicked.connect(self.confirmar_aluguel)

        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.clicked.connect(self.reject)

        botoes.addStretch()
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(self.botao_confirmar)

        layout.addLayout(botoes)

    def formatar_moeda(self, valor):
        return f"R$ {valor:.2f}".replace(".", ",")

    def atualizar_valor(self):
        valor = self.filme.preco_diaria * self.campo_dias.value()
        self.label_valor.setText(self.formatar_moeda(valor))

    def confirmar_aluguel(self):
        cliente_id = self.combo_clientes.currentData()
        dias = self.campo_dias.value()

        if cliente_id is None:
            QMessageBox.warning(self, "Cliente obrigatório", "Selecione um cliente para realizar o aluguel.")
            return

        resposta = QMessageBox.question(self, "Confirmar aluguel", f"Deseja alugar '{self.filme.titulo}' por {dias} dia(s)?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            aluguel = self.locadora.alugar_filme(self.filme.id, cliente_id, dias)

        except (ValueError, LookupError, OSError, RuntimeError) as erro:
            QMessageBox.warning(self, "Não foi possível realizar o aluguel", str(erro))
            return

        self.aluguel_realizado.emit()

        QMessageBox.information(self, "Aluguel realizado", f"Aluguel #{aluguel.id} realizado com sucesso.\nValor total: {self.formatar_moeda(aluguel.valor_total)}")

        self.accept()