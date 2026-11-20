
import sys

from PySide6.QtWidgets import QApplication

from servicos.locadora_remota import LocadoraRemota
from interfaces.janela_principal import JanelaPrincipal


def main():
    app = QApplication(sys.argv)

    locadora = LocadoraRemota()
    janela = JanelaPrincipal(locadora)

    janela.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
