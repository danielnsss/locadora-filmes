import sys

from PySide6.QtWidgets import QApplication

from servicos.locadora import Locadora
from interfaces.janela_principal import JanelaPrincipal


def main():
    app = QApplication(sys.argv)

    locadora = Locadora()
    janela = JanelaPrincipal(locadora)

    janela.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()