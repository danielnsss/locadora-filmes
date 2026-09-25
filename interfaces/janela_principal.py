
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QToolBar

from modelos.filme import Filme
from interfaces.janela_aluguel import JanelaAluguel

from interfaces.janela_cadastro import JanelaCadastro
from interfaces.janela_historico import JanelaHistorico

class JanelaPrincipal(QMainWindow):
    def __init__(self, locadora):
        super().__init__()

        self.locadora = locadora
        self.filmes = []

        self.setWindowTitle("Locadora de Filmes")
        self.resize(1000, 650)

        self.criar_interface()
        self.criar_menu()
        self.criar_barra_ferramentas()
        self.atualizar_catalogo()

    def criar_interface(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        titulo = QLabel("Catálogo de Filmes")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        barra_pesquisa = QHBoxLayout()

        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText("Pesquisar filme pelo título...")
        self.campo_pesquisa.textChanged.connect(self.pesquisar_filmes)

        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self.atualizar_catalogo)

        barra_pesquisa.addWidget(self.campo_pesquisa)
        barra_pesquisa.addWidget(botao_atualizar)
        layout.addLayout(barra_pesquisa)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Título", "Gênero", "Ano", "Diária", "Disponíveis"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.cellDoubleClicked.connect(self.abrir_aluguel)

        layout.addWidget(self.tabela)
        self.statusBar().showMessage("Locadora de Filmes")

    def criar_menu(self):
        menu_arquivo = self.menuBar().addMenu("Arquivo")

        acao_sair = QAction("Sair", self)
        acao_sair.setShortcut("Ctrl+Q")
        acao_sair.triggered.connect(self.close)
        menu_arquivo.addAction(acao_sair)

        menu_filmes = self.menuBar().addMenu("Filmes")

        acao_atualizar = QAction("Atualizar catálogo", self)
        acao_atualizar.triggered.connect(self.atualizar_catalogo)
        menu_filmes.addAction(acao_atualizar)

        menu_ajuda = self.menuBar().addMenu("Ajuda")

        acao_sobre = QAction("Sobre", self)
        acao_sobre.triggered.connect(self.exibir_sobre)
        menu_ajuda.addAction(acao_sobre)

        menu_cadastro = self.menuBar().addMenu("Cadastro")

        acao_cadastrar = QAction("Cadastrar filme ou cliente", self)
        acao_cadastrar.triggered.connect(self.abrir_cadastro)
        menu_cadastro.addAction(acao_cadastrar)

        menu_locacoes = self.menuBar().addMenu("Locações")
        acao_historico = QAction("Histórico e devoluções", self)
        acao_historico.triggered.connect(self.abrir_historico)
        menu_locacoes.addAction(acao_historico)

    def criar_barra_ferramentas(self):
        barra = QToolBar("Ferramentas")
        barra.setMovable(False)
        self.addToolBar(barra)

        acao_atualizar = QAction("Atualizar", self)
        acao_atualizar.triggered.connect(self.atualizar_catalogo)
        barra.addAction(acao_atualizar)

        self.acao_cadastrar = QAction("Cadastrar", self)
        self.acao_cadastrar.triggered.connect(self.abrir_cadastro)
        barra.addAction(self.acao_cadastrar)

        self.acao_alugar = QAction("Alugar", self)
        self.acao_alugar.triggered.connect(lambda: self.abrir_aluguel())
        barra.addAction(self.acao_alugar)

        self.acao_historico = QAction("Histórico", self)
        self.acao_historico.triggered.connect(self.abrir_historico)
        barra.addAction(self.acao_historico)

    def abrir_historico(self):
        janela = JanelaHistorico(self.locadora, self)
        janela.devolucao_realizada.connect(self.atualizar_catalogo)
        janela.exec()

    def abrir_cadastro(self):
        janela = JanelaCadastro(self.locadora, self)
        janela.filme_cadastrado.connect(self.atualizar_catalogo)
        janela.cliente_cadastrado.connect(lambda: self.statusBar().showMessage("Cliente cadastrado com sucesso.", 5000))
        janela.exec()

    def atualizar_catalogo(self):
        try:
            self.filmes = self.locadora.listar_filmes()
            mensagem = f"{len(self.filmes)} filme(s) encontrado(s)."

        except NotImplementedError:
            self.filmes = [
                Filme(1, "Interestelar", "Ficção científica", 2014, "Uma viagem pelo espaço.", 5.0, 3),
                Filme(2, "A Origem", "Ficção científica", 2010, "Um filme sobre sonhos.", 6.0, 2)
            ]
            mensagem = "Modo de demonstração: serviço ainda não implementado."

        except (OSError, ValueError) as erro:
            self.filmes = []
            mensagem = "Não foi possível carregar o catálogo."
            QMessageBox.warning(self, "Erro", str(erro))

        self.pesquisar_filmes(self.campo_pesquisa.text())
        self.statusBar().showMessage(mensagem)

    def pesquisar_filmes(self, termo):
        termo = termo.strip().casefold()
        filmes_filtrados = [filme for filme in self.filmes if termo in filme.titulo.casefold()]

        self.tabela.setRowCount(len(filmes_filtrados))

        for linha, filme in enumerate(filmes_filtrados):
            valores = [filme.titulo, filme.genero, str(filme.ano), f"R$ {filme.preco_diaria:.2f}".replace(".", ","), str(filme.quantidade_disponivel)]

            for coluna, valor in enumerate(valores):
                item = QTableWidgetItem(valor)
                if coluna == 0:
                    item.setData(Qt.ItemDataRole.UserRole, filme.id)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(linha, coluna, item)

    def abrir_aluguel(self, linha=None, coluna=None):
        if linha is None:
            linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.warning(self, "Seleção obrigatória", "Selecione um filme para realizar o aluguel.")
            return

        item = self.tabela.item(linha, 0)

        if item is None:
            QMessageBox.warning(self, "Erro", "Não foi possível identificar o filme selecionado.")
            return

        filme_id = item.data(Qt.ItemDataRole.UserRole)

        if filme_id is None:
            QMessageBox.warning(self, "Erro", "O filme selecionado não possui um identificador válido.")
            return

        try:
            janela = JanelaAluguel(self.locadora, filme_id, self)

        except (ValueError, LookupError, OSError) as erro:
            QMessageBox.warning(self, "Erro ao abrir aluguel", str(erro))
            return

        janela.aluguel_realizado.connect(self.atualizar_catalogo)
        janela.exec()

    def abrir_detalhes_filme(self, linha, coluna):
        titulo = self.tabela.item(linha, 0).text()
        QMessageBox.information(self, "Filme selecionado", f"Filme: {titulo}\nA funcionalidade de aluguel será integrada posteriormente.")

    def exibir_sobre(self):
        QMessageBox.information(self, "Sobre", "Locadora de Filmes\nProjeto de Programação Orientada a Objetos II.")

    def closeEvent(self, evento):
        resposta = QMessageBox.question(self, "Sair", "Deseja realmente fechar a aplicação?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if resposta == QMessageBox.StandardButton.Yes:
            evento.accept()
        else:
            evento.ignore()