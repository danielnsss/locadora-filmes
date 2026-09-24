
from armazenamento.json_repository import JSONRepository
from modelos.filme import Filme
from modelos.cliente import Cliente
from datetime import date, timedelta
from modelos.aluguel import Aluguel

class Locadora:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio if repositorio is not None else JSONRepository()

    def listar_filmes(self):
        registros = self.repositorio.listar("filmes")
        return [Filme.from_dict(registro) for registro in registros]

    def obter_filme(self, filme_id):
        if type(filme_id) is not int or filme_id <= 0:
            raise ValueError("O ID do filme deve ser um inteiro positivo.")

        for filme in self.listar_filmes():
            if filme.id == filme_id:
                return filme

        raise LookupError("Filme não encontrado.")

    def buscar_filmes(self, termo):
        if not isinstance(termo, str):
            raise ValueError("O termo da pesquisa deve ser um texto.")

        termo = termo.strip().casefold()
        return [filme for filme in self.listar_filmes() if termo in filme.titulo.casefold()]

    def cadastrar_filme(self, titulo, genero, ano, sinopse, preco_diaria, quantidade_total):
        novo_id = self.repositorio.proximo_id("filmes")

        filme = Filme(novo_id, titulo, genero, ano, sinopse, preco_diaria, quantidade_total)

        registros = self.repositorio.listar("filmes")
        registros.append(filme.to_dict())

        self.repositorio.salvar("filmes", registros)

        return filme

    def cadastrar_cliente(self, nome, telefone):
        novo_id = self.repositorio.proximo_id("clientes")

        cliente = Cliente(novo_id, nome, telefone)

        registros = self.repositorio.listar("clientes")
        registros.append(cliente.to_dict())

        self.repositorio.salvar("clientes", registros)

        return cliente

    def listar_clientes(self):
        registros = self.repositorio.listar("clientes")
        return [Cliente.from_dict(registro) for registro in registros]

    
    def alugar_filme(self, filme_id, cliente_id, dias):
        if type(dias) is not int or dias <= 0:
            raise ValueError("A quantidade de dias deve ser um inteiro positivo.")

        if type(cliente_id) is not int or cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser um inteiro positivo.")

        filme = self.obter_filme(filme_id)

        if not any(cliente.id == cliente_id for cliente in self.listar_clientes()):
            raise LookupError("Cliente não encontrado.")

        if filme.quantidade_disponivel <= 0:
            raise ValueError("Não há exemplares disponíveis para aluguel.")

        hoje = date.today()
        data_prevista = hoje + timedelta(days=dias)

        aluguel = Aluguel(
            id=self.repositorio.proximo_id("alugueis"),
            filme_id=filme.id,
            cliente_id=cliente_id,
            data_aluguel=hoje.isoformat(),
            data_devolucao_prevista=data_prevista.isoformat(),
            valor_total=round(filme.preco_diaria * dias, 2)
        )

        alugueis_antigos = self.repositorio.listar("alugueis")
        alugueis_novos = alugueis_antigos + [aluguel.to_dict()]

        filmes_novos = self.repositorio.listar("filmes")
        filme.quantidade_disponivel -= 1

        for indice, registro in enumerate(filmes_novos):
            if registro["id"] == filme.id:
                filmes_novos[indice] = filme.to_dict()
                break

        self._salvar_movimento(alugueis_antigos, alugueis_novos, filmes_novos)

        return aluguel

    def devolver_filme(self, aluguel_id):
        if type(aluguel_id) is not int or aluguel_id <= 0:
            raise ValueError("O ID do aluguel deve ser um inteiro positivo.")

        alugueis_antigos = self.repositorio.listar("alugueis")
        alugueis_novos = [registro.copy() for registro in alugueis_antigos]

        indice_aluguel = next((indice for indice, registro in enumerate(alugueis_novos) if registro["id"] == aluguel_id), None)

        if indice_aluguel is None:
            raise LookupError("Aluguel não encontrado.")

        aluguel = Aluguel.from_dict(alugueis_novos[indice_aluguel])

        if aluguel.status != "ativo":
            raise ValueError("Este aluguel já foi devolvido.")

        filme = self.obter_filme(aluguel.filme_id)

        if filme.quantidade_disponivel >= filme.quantidade_total:
            raise ValueError("Estoque inconsistente: não é possível devolver este exemplar.")

        aluguel.status = "devolvido"
        aluguel.data_devolucao_real = date.today().isoformat()
        alugueis_novos[indice_aluguel] = aluguel.to_dict()

        filmes_novos = self.repositorio.listar("filmes")
        filme.quantidade_disponivel += 1

        for indice, registro in enumerate(filmes_novos):
            if registro["id"] == filme.id:
                filmes_novos[indice] = filme.to_dict()
                break

        self._salvar_movimento(alugueis_antigos, alugueis_novos, filmes_novos)

        return aluguel

    def listar_alugueis(self, status=None):
        if status is not None and status not in ("ativo", "devolvido"):
            raise ValueError("O status deve ser 'ativo' ou 'devolvido'.")

        registros = self.repositorio.listar("alugueis")
        alugueis = [Aluguel.from_dict(registro) for registro in registros]

        if status is not None:
            alugueis = [aluguel for aluguel in alugueis if aluguel.status == status]

        return alugueis

    def _salvar_movimento(self, alugueis_antigos, alugueis_novos, filmes_novos):
        self.repositorio.salvar("alugueis", alugueis_novos)

        try:
            self.repositorio.salvar("filmes", filmes_novos)

        except Exception as erro:
            try:
                self.repositorio.salvar("alugueis", alugueis_antigos)

            except Exception as erro_reversao:
                raise RuntimeError("Falha ao gravar e reverter a operação. Verifique a consistência dos arquivos JSON.") from erro_reversao

            raise RuntimeError("A operação não foi concluída. O registro de aluguel foi revertido.") from erro