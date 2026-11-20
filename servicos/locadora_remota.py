
import os

import requests

from modelos.aluguel import Aluguel
from modelos.cliente import Cliente
from modelos.filme import Filme


class LocadoraRemota:
    def __init__(self, url_base=None):
        self.url_base = (
            url_base or os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
        ).rstrip("/")

    def _requisicao(self, metodo, caminho, dados=None, parametros=None):
        try:
            resposta = requests.request(
                metodo,
                f"{self.url_base}{caminho}",
                json=dados,
                params=parametros,
                timeout=(3, 10)
            )
        except requests.RequestException as erro:
            raise OSError(
                "Não foi possível estabelecer comunicação com a API."
            ) from erro

        if resposta.status_code >= 400:
            try:
                conteudo = resposta.json()
                detalhe = conteudo.get("detail") if isinstance(conteudo, dict) else None
            except ValueError:
                detalhe = None

            if isinstance(detalhe, list):
                mensagem = "; ".join(
                    item.get("msg", "Dados inválidos.")
                    for item in detalhe
                    if isinstance(item, dict)
                ) or "Dados inválidos."
            elif isinstance(detalhe, str):
                mensagem = detalhe
            else:
                mensagem = f"Erro HTTP {resposta.status_code}."

            if resposta.status_code == 404:
                raise LookupError(mensagem)

            if resposta.status_code in (409, 422):
                raise ValueError(mensagem)

            raise RuntimeError(mensagem)

        if resposta.status_code == 204:
            return None

        try:
            return resposta.json()
        except ValueError as erro:
            raise RuntimeError("A API retornou uma resposta inválida.") from erro

    def listar_filmes(self):
        dados = self._requisicao("GET", "/filmes")
        return [Filme.from_dict(registro) for registro in dados]

    def obter_filme(self, filme_id):
        dados = self._requisicao("GET", f"/filmes/{filme_id}")
        return Filme.from_dict(dados)

    def buscar_filmes(self, termo):
        if not isinstance(termo, str):
            raise ValueError("O termo da pesquisa deve ser um texto.")

        dados = self._requisicao(
            "GET", "/filmes", parametros={"termo": termo}
        )
        return [Filme.from_dict(registro) for registro in dados]

    def cadastrar_filme(self, titulo, genero, ano, sinopse, preco_diaria, quantidade_total):
        dados = {
            "titulo": titulo,
            "genero": genero,
            "ano": ano,
            "sinopse": sinopse,
            "preco_diaria": preco_diaria,
            "quantidade_total": quantidade_total
        }
        resposta = self._requisicao("POST", "/filmes", dados=dados)
        return Filme.from_dict(resposta)

    def excluir_filme(self, filme_id):
        filme = self.obter_filme(filme_id)
        self._requisicao("DELETE", f"/filmes/{filme_id}")
        return filme

    def listar_clientes(self):
        dados = self._requisicao("GET", "/clientes")
        return [Cliente.from_dict(registro) for registro in dados]

    def obter_cliente(self, cliente_id):
        dados = self._requisicao("GET", f"/clientes/{cliente_id}")
        return Cliente.from_dict(dados)

    def cadastrar_cliente(self, nome, telefone):
        dados = {
            "nome": nome,
            "telefone": telefone
        }
        resposta = self._requisicao("POST", "/clientes", dados=dados)
        return Cliente.from_dict(resposta)

    def excluir_cliente(self, cliente_id):
        cliente = self.obter_cliente(cliente_id)
        self._requisicao("DELETE", f"/clientes/{cliente_id}")
        return cliente

    def listar_alugueis(self, status=None):
        parametros = {"status": status} if status is not None else None
        dados = self._requisicao(
            "GET", "/alugueis", parametros=parametros
        )
        return [Aluguel.from_dict(registro) for registro in dados]

    def alugar_filme(self, filme_id, cliente_id, dias):
        dados = {
            "filme_id": filme_id,
            "cliente_id": cliente_id,
            "dias": dias
        }
        resposta = self._requisicao("POST", "/alugueis", dados=dados)
        return Aluguel.from_dict(resposta)

    def devolver_filme(self, aluguel_id):
        resposta = self._requisicao(
            "PATCH", f"/alugueis/{aluguel_id}/devolucao"
        )
        return Aluguel.from_dict(resposta)
