
import json
import os
import tempfile

from pathlib import Path


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

        for caminho in self.arquivos.values():
            if not caminho.exists():
                with caminho.open("x", encoding="utf-8") as arquivo:
                    json.dump([], arquivo, ensure_ascii=False, indent=4)

    def _obter_caminho(self, tipo):
        if tipo not in self.arquivos:
            raise ValueError("Tipo de coleção inválido.")

        return self.arquivos[tipo]

    def _validar_registros(self, registros):
        if not isinstance(registros, list):
            raise ValueError("Os registros devem formar uma lista.")

        ids = set()

        for registro in registros:
            if not isinstance(registro, dict):
                raise ValueError("Cada registro deve ser um dicionário.")

            id = registro.get("id")

            if type(id) is not int or id <= 0:
                raise ValueError("Cada registro deve possuir um ID inteiro positivo.")

            if id in ids:
                raise ValueError("Existem identificadores duplicados.")

            ids.add(id)

    def listar(self, tipo):
        caminho = self._obter_caminho(tipo)

        with caminho.open("r", encoding="utf-8") as arquivo:
            registros = json.load(arquivo)

        self._validar_registros(registros)

        return registros

    def salvar(self, tipo, registros):
        caminho = self._obter_caminho(tipo)

        self._validar_registros(registros)

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

    def proximo_id(self, tipo):
        registros = self.listar(tipo)

        if not registros:
            return 1

        return max(registro["id"] for registro in registros) + 1