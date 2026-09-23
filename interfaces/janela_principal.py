from PySide6.QtWidgets import QMainWindow, QLabel


class JanelaPrincipal(QMainWindow):

    def __init__(self, locadora):
        super().__init__()

        self.locadora = locadora

        self.setWindowTitle("Locadora de Filmes")
        self.resize(1000, 650)

        self.setCentralWidget(
            QLabel("Bem-vindo à Locadora de Filmes!")
        )