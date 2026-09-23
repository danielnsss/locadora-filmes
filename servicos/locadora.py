
class Locadora:

    def __init__(self, repositorio=None):
        self.repositorio = repositorio

    def listar_filmes(self):
        raise NotImplementedError

    def obter_filme(self, filme_id):
        raise NotImplementedError

    def buscar_filmes(self, termo):
        raise NotImplementedError

    def cadastrar_filme(
        self,
        titulo,
        genero,
        ano,
        sinopse,
        preco_diaria,
        quantidade_total
    ):
        raise NotImplementedError

    def cadastrar_cliente(self, nome, telefone):
        raise NotImplementedError

    def listar_clientes(self):
        raise NotImplementedError

    def alugar_filme(self, filme_id, cliente_id, dias):
        raise NotImplementedError

    def devolver_filme(self, aluguel_id):
        raise NotImplementedError

    def listar_alugueis(self, status=None):
        raise NotImplementedError