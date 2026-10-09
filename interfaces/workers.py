from PySide6.QtCore import QThread, Signal


class CarregamentoThread(QThread):
    concluido = Signal(object)
    erro = Signal(str)
    nao_implementado = Signal()

    def __init__(self, funcao, parent=None):
        super().__init__(parent)
        self.funcao = funcao

    def run(self):
        try:
            resultado = self.funcao()

        except NotImplementedError:
            self.nao_implementado.emit()

        except (OSError, ValueError, LookupError, RuntimeError) as erro:
            self.erro.emit(str(erro))

        else:
            self.concluido.emit(resultado)