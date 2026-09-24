
from datetime import date

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox


class JanelaCadastro(QDialog):
    filme_cadastrado = Signal()
    cliente_cadastrado = Signal()

    def __init__(self, locadora, parent=None):
        super().__init__(parent)

        self.locadora = locadora

        self.setWindowTitle("Cadastro - Locadora de Filmes")
        self.setMinimumWidth(500)
        self.resize(550, 450)

        self.criar_interface()

    def criar_interface(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Cadastro")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        self.abas = QTabWidget()
        self.abas.addTab(self.criar_aba_filmes(), "Filmes")
        self.abas.addTab(self.criar_aba_clientes(), "Clientes")

        layout.addWidget(self.abas)

        botao_fechar = QPushButton("Fechar")
        botao_fechar.clicked.connect(self.close)
        layout.addWidget(botao_fechar)

    def criar_aba_filmes(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        formulario = QFormLayout()

        self.campo_titulo = QLineEdit()
        self.campo_titulo.setPlaceholderText("Título do filme")

        self.campo_genero = QLineEdit()
        self.campo_genero.setPlaceholderText("Gênero do filme")

        self.campo_ano = QSpinBox()
        self.campo_ano.setRange(1, 9999)
        self.campo_ano.setValue(date.today().year)

        self.campo_sinopse = QPlainTextEdit()
        self.campo_sinopse.setPlaceholderText("Sinopse do filme")
        self.campo_sinopse.setMaximumHeight(90)

        self.campo_preco = QDoubleSpinBox()
        self.campo_preco.setRange(0.0, 1000000.0)
        self.campo_preco.setDecimals(2)
        self.campo_preco.setSingleStep(1.0)
        self.campo_preco.setPrefix("R$ ")

        self.campo_quantidade = QSpinBox()
        self.campo_quantidade.setRange(0, 1000000)
        self.campo_quantidade.setValue(1)

        formulario.addRow("Título:", self.campo_titulo)
        formulario.addRow("Gênero:", self.campo_genero)
        formulario.addRow("Ano:", self.campo_ano)
        formulario.addRow("Sinopse:", self.campo_sinopse)
        formulario.addRow("Preço da diária:", self.campo_preco)
        formulario.addRow("Quantidade:", self.campo_quantidade)

        layout.addLayout(formulario)

        botao_cadastrar = QPushButton("Cadastrar filme")
        botao_cadastrar.clicked.connect(self.cadastrar_filme)
        layout.addWidget(botao_cadastrar)

        layout.addStretch()
        return pagina

    def criar_aba_clientes(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        formulario = QFormLayout()

        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText("Nome completo")

        self.campo_telefone = QLineEdit()
        self.campo_telefone.setPlaceholderText("Telefone com DDD")

        formulario.addRow("Nome:", self.campo_nome)
        formulario.addRow("Telefone:", self.campo_telefone)

        layout.addLayout(formulario)

        botao_cadastrar = QPushButton("Cadastrar cliente")
        botao_cadastrar.clicked.connect(self.cadastrar_cliente)
        layout.addWidget(botao_cadastrar)

        layout.addStretch()
        return pagina

    def cadastrar_filme(self):
        titulo = self.campo_titulo.text().strip()
        genero = self.campo_genero.text().strip()
        ano = self.campo_ano.value()
        sinopse = self.campo_sinopse.toPlainText().strip()
        preco_diaria = self.campo_preco.value()
        quantidade_total = self.campo_quantidade.value()

        if not titulo or not genero:
            QMessageBox.warning(self, "Campos obrigatórios", "Informe o título e o gênero do filme.")
            return

        try:
            metodo = getattr(self.locadora, "cadastrar_filme", None)

            if not callable(metodo):
                raise NotImplementedError("O serviço de cadastro de filmes ainda não está disponível.")

            metodo(titulo, genero, ano, sinopse, preco_diaria, quantidade_total)

        except (ValueError, OSError, NotImplementedError) as erro:
            QMessageBox.warning(self, "Não foi possível cadastrar", str(erro))
            return

        self.filme_cadastrado.emit()
        QMessageBox.information(self, "Cadastro realizado", "Filme cadastrado com sucesso.")
        self.limpar_campos_filme()

    def cadastrar_cliente(self):
        nome = self.campo_nome.text().strip()
        telefone = self.campo_telefone.text().strip()

        if not nome or not telefone:
            QMessageBox.warning(self, "Campos obrigatórios", "Informe o nome e o telefone do cliente.")
            return

        try:
            metodo = getattr(self.locadora, "cadastrar_cliente", None)

            if not callable(metodo):
                raise NotImplementedError("O serviço de cadastro de clientes ainda não está disponível.")

            metodo(nome, telefone)

        except (ValueError, OSError, NotImplementedError) as erro:
            QMessageBox.warning(self, "Não foi possível cadastrar", str(erro))
            return

        self.cliente_cadastrado.emit()
        QMessageBox.information(self, "Cadastro realizado", "Cliente cadastrado com sucesso.")
        self.limpar_campos_cliente()

    def limpar_campos_filme(self):
        self.campo_titulo.clear()
        self.campo_genero.clear()
        self.campo_ano.setValue(date.today().year)
        self.campo_sinopse.clear()
        self.campo_preco.setValue(0.0)
        self.campo_quantidade.setValue(1)
        self.campo_titulo.setFocus()

    def limpar_campos_cliente(self):
        self.campo_nome.clear()
        self.campo_telefone.clear()
        self.campo_nome.setFocus()