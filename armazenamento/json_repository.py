import json
import os
import tempfile

from pathlib import Path

from modelos.aluguel import Aluguel
from modelos.cliente import Cliente
from modelos.filme import Filme


class JSONRepository:
    def __init__(self, diretorio_dados=None):
        if diretorio_dados is None:
            diretorio_dados = Path(__file__).resolve().parent.parent / "dados"

        self.diretorio_dados = Path(diretorio_dados)
        self.diretorio_dados.mkdir(parents=True, exist_ok=True)

        self.arquivos = {
            "filmes": self.diretorio_dados / "filmes.json",
            "clientes": self.diretorio_dados / "clientes.json",
            "alugueis": self.diretorio_dados / "alugueis.json"
        }

        self.modelos = {"filmes": Filme, "clientes": Cliente, "alugueis": Aluguel}
        self.campos = {
            "filmes": {"id", "titulo", "genero", "ano", "sinopse", "preco_diaria", "quantidade_total", "quantidade_disponivel"},
            "clientes": {"id", "nome", "telefone"},
            "alugueis": {"id", "filme_id", "cliente_id", "data_aluguel", "data_devolucao_prevista", "data_devolucao_real", "valor_total", "status"}
        }

        for caminho in self.arquivos.values():
            if not caminho.exists():
                with caminho.open("x", encoding="utf-8") as arquivo:
                    json.dump([], arquivo, ensure_ascii=False, indent=4)

    def _obter_caminho(self, tipo):
        if tipo not in self.arquivos:
            raise ValueError("Tipo de coleção inválido.")

        return self.arquivos[tipo]

    def _validar_registros(self, registros, tipo):
        if not isinstance(registros, list):
            raise ValueError("Os registros devem formar uma lista.")

        ids = set()

        for indice, registro in enumerate(registros, start=1):
            if not isinstance(registro, dict):
                raise ValueError(f"O registro {indice} de {tipo} deve ser um dicionário.")

            id = registro.get("id")

            if type(id) is not int or id <= 0:
                raise ValueError(f"O registro {indice} de {tipo} deve possuir um ID inteiro positivo.")

            if id in ids:
                raise ValueError(f"Existem identificadores duplicados na coleção {tipo}.")

            ids.add(id)

            if any(not isinstance(campo, str) for campo in registro):
                raise ValueError(f"O registro {indice} de {tipo} possui nomes de campos inválidos.")

            if set(registro) != self.campos[tipo]:
                ausentes = sorted(self.campos[tipo] - set(registro))
                extras = sorted(set(registro) - self.campos[tipo])
                raise ValueError(f"O registro {indice} de {tipo} possui campos incorretos. Ausentes: {ausentes}; extras: {extras}.")

            try:
                self.modelos[tipo].from_dict(registro)
            except (ValueError, TypeError, KeyError) as erro:
                raise ValueError(f"O registro {indice} de {tipo} contém dados inválidos: {erro}") from erro

    def listar(self, tipo):
        caminho = self._obter_caminho(tipo)

        with caminho.open("r", encoding="utf-8") as arquivo:
            registros = json.load(arquivo)

        self._validar_registros(registros, tipo)

        return registros

    def salvar(self, tipo, registros):
        caminho = self._obter_caminho(tipo)

        self._validar_registros(registros, tipo)

        # Impede sobrescrever silenciosamente um arquivo inválido.
        self.listar(tipo)

        caminho_temporario = None

        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.diretorio_dados, prefix=f".{tipo}_", suffix=".tmp", delete=False) as arquivo:
                caminho_temporario = Path(arquivo.name)
                json.dump(registros, arquivo, ensure_ascii=False, indent=4, allow_nan=False)
                arquivo.flush()
                os.fsync(arquivo.fileno())

            os.replace(caminho_temporario, caminho)

        finally:
            if caminho_temporario is not None:
                caminho_temporario.unlink(missing_ok=True)

    def excluir(self, tipo, registro_id):
        self._obter_caminho(tipo)

        if type(registro_id) is not int or registro_id <= 0:
            raise ValueError("O ID do registro deve ser um inteiro positivo.")

        registros = self.listar(tipo)
        registros_novos = [registro for registro in registros if registro["id"] != registro_id]

        if len(registros_novos) == len(registros):
            raise LookupError("Registro não encontrado.")

        self.salvar(tipo, registros_novos)

    def proximo_id(self, tipo):
        registros = self.listar(tipo)

        if not registros:
            return 1

        return max(registro["id"] for registro in registros) + 1
