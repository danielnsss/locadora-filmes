from sqlalchemy import select
from modelos.cliente import Cliente
from modelos.filme import Filme
from datetime import date, timedelta

from modelos.aluguel import Aluguel

from banco.modelos_db import AluguelDB, ClienteDB, FilmeDB


class RepositorioBanco:
    def __init__(self, sessao):
        self.sessao = sessao

    def listar_filmes(self):
        consulta = select(FilmeDB).order_by(FilmeDB.id)
        return self.sessao.scalars(consulta).all()

    def obter_filme(self, filme_id):
        return self.sessao.get(FilmeDB, filme_id)

    def buscar_filmes(self, termo):
        if not isinstance(termo, str):
            raise ValueError("O termo da pesquisa deve ser um texto.")

        termo = termo.strip().casefold()
        return [
            filme for filme in self.listar_filmes()
            if termo in filme.titulo.casefold()
        ]

    def listar_clientes(self):
        consulta = select(ClienteDB).order_by(ClienteDB.id)
        return self.sessao.scalars(consulta).all()

    def obter_cliente(self, cliente_id):
        return self.sessao.get(ClienteDB, cliente_id)

    def listar_alugueis(self, status=None):
        if status is not None and status not in ("ativo", "devolvido"):
            raise ValueError("O status deve ser 'ativo' ou 'devolvido'.")

        consulta = select(AluguelDB).order_by(AluguelDB.id)

        if status is not None:
            consulta = consulta.where(AluguelDB.status == status)

        return self.sessao.scalars(consulta).all()

    def cadastrar_filme(self, titulo, genero, ano, sinopse, preco_diaria, quantidade_total):
        filme = Filme(
            id=1,
            titulo=titulo,
            genero=genero,
            ano=ano,
            sinopse=sinopse,
            preco_diaria=preco_diaria,
            quantidade_total=quantidade_total
        )

        registro = FilmeDB(
            titulo=filme.titulo,
            genero=filme.genero,
            ano=filme.ano,
            sinopse=filme.sinopse,
            preco_diaria=filme.preco_diaria,
            quantidade_total=filme.quantidade_total,
            quantidade_disponivel=filme.quantidade_disponivel
        )

        self.sessao.add(registro)
        self.sessao.flush()

        return registro


    def cadastrar_cliente(self, nome, telefone):
        cliente = Cliente(id=1, nome=nome, telefone=telefone)

        registro = ClienteDB(
            nome=cliente.nome,
            telefone=cliente.telefone
        )

        self.sessao.add(registro)
        self.sessao.flush()

        return registro

    def excluir_filme(self, filme_id):
        if type(filme_id) is not int or filme_id <= 0:
            raise ValueError("O ID do filme deve ser um inteiro positivo.")

        filme = self.obter_filme(filme_id)

        if filme is None:
            raise LookupError("Filme não encontrado.")

        aluguel_id = self.sessao.scalar(
            select(AluguelDB.id)
            .where(AluguelDB.filme_id == filme_id)
            .limit(1)
        )

        if aluguel_id is not None:
            raise ValueError("Não é possível excluir um filme que possui aluguel registrado.")

        self.sessao.delete(filme)
        self.sessao.flush()

        return filme


    def excluir_cliente(self, cliente_id):
        if type(cliente_id) is not int or cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser um inteiro positivo.")

        cliente = self.obter_cliente(cliente_id)

        if cliente is None:
            raise LookupError("Cliente não encontrado.")

        aluguel_id = self.sessao.scalar(
            select(AluguelDB.id)
            .where(AluguelDB.cliente_id == cliente_id)
            .limit(1)
        )

        if aluguel_id is not None:
            raise ValueError("Não é possível excluir um cliente que possui aluguel registrado.")

        self.sessao.delete(cliente)
        self.sessao.flush()

        return cliente

    def alugar_filme(self, filme_id, cliente_id, dias):
        if type(filme_id) is not int or filme_id <= 0:
            raise ValueError("O ID do filme deve ser um inteiro positivo.")

        if type(cliente_id) is not int or cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser um inteiro positivo.")

        if type(dias) is not int or dias <= 0:
            raise ValueError("A quantidade de dias deve ser um inteiro positivo.")

        filme = self.sessao.scalar(
            select(FilmeDB)
            .where(FilmeDB.id == filme_id)
            .with_for_update()
        )

        if filme is None:
            raise LookupError("Filme não encontrado.")

        cliente = self.obter_cliente(cliente_id)

        if cliente is None:
            raise LookupError("Cliente não encontrado.")

        if filme.quantidade_disponivel <= 0:
            raise ValueError("Não há exemplares disponíveis para aluguel.")

        hoje = date.today()
        data_prevista = hoje + timedelta(days=dias)

        aluguel = Aluguel(
            id=1,
            filme_id=filme.id,
            cliente_id=cliente.id,
            data_aluguel=hoje.isoformat(),
            data_devolucao_prevista=data_prevista.isoformat(),
            valor_total=round(filme.preco_diaria * dias, 2)
        )

        registro = AluguelDB(
            filme_id=aluguel.filme_id,
            cliente_id=aluguel.cliente_id,
            data_aluguel=hoje,
            data_devolucao_prevista=data_prevista,
            data_devolucao_real=None,
            valor_total=aluguel.valor_total,
            status=aluguel.status
        )

        filme.quantidade_disponivel -= 1

        self.sessao.add(registro)
        self.sessao.flush()

        return registro

    def devolver_filme(self, aluguel_id):
        if type(aluguel_id) is not int or aluguel_id <= 0:
            raise ValueError("O ID do aluguel deve ser um inteiro positivo.")

        aluguel = self.sessao.scalar(
            select(AluguelDB)
            .where(AluguelDB.id == aluguel_id)
            .with_for_update()
        )

        if aluguel is None:
            raise LookupError("Aluguel não encontrado.")

        if aluguel.status != "ativo":
            raise ValueError("Este aluguel já foi devolvido.")

        filme = self.sessao.scalar(
            select(FilmeDB)
            .where(FilmeDB.id == aluguel.filme_id)
            .with_for_update()
        )

        if filme is None:
            raise LookupError("Filme não encontrado.")

        if filme.quantidade_disponivel >= filme.quantidade_total:
            raise ValueError("O estoque do filme está inconsistente.")

        aluguel.status = "devolvido"
        aluguel.data_devolucao_real = date.today()

        filme.quantidade_disponivel += 1

        self.sessao.flush()

        return aluguel