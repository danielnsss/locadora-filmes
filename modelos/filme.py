import math


class Filme:
    def __init__(self, id, titulo, genero, ano, sinopse, preco_diaria, quantidade_total, quantidade_disponivel=None):
        if type(id) is not int or id <= 0:
            raise ValueError("O ID deve ser um inteiro positivo.")

        if not isinstance(titulo, str) or not titulo.strip():
            raise ValueError("O título não pode estar vazio.")

        if not isinstance(genero, str) or not genero.strip():
            raise ValueError("O gênero não pode estar vazio.")

        if type(ano) is not int or not 1 <= ano <= 9999:
            raise ValueError("O ano informado é inválido.")

        if not isinstance(sinopse, str):
            raise ValueError("A sinopse deve ser um texto.")

        if type(preco_diaria) not in (int, float) or not math.isfinite(preco_diaria) or preco_diaria < 0:
            raise ValueError("O preço da diária é inválido.")

        if type(quantidade_total) is not int or quantidade_total < 0:
            raise ValueError("A quantidade total é inválida.")

        if quantidade_disponivel is None:
            quantidade_disponivel = quantidade_total

        if type(quantidade_disponivel) is not int or not 0 <= quantidade_disponivel <= quantidade_total:
            raise ValueError("A quantidade disponível é inválida.")

        self.id = id
        self.titulo = titulo.strip()
        self.genero = genero.strip()
        self.ano = ano
        self.sinopse = sinopse.strip()
        self.preco_diaria = float(preco_diaria)
        self.quantidade_total = quantidade_total
        self.quantidade_disponivel = quantidade_disponivel

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "genero": self.genero,
            "ano": self.ano,
            "sinopse": self.sinopse,
            "preco_diaria": self.preco_diaria,
            "quantidade_total": self.quantidade_total,
            "quantidade_disponivel": self.quantidade_disponivel
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(
            id=dados["id"],
            titulo=dados["titulo"],
            genero=dados["genero"],
            ano=dados["ano"],
            sinopse=dados["sinopse"],
            preco_diaria=dados["preco_diaria"],
            quantidade_total=dados["quantidade_total"],
            quantidade_disponivel=dados["quantidade_disponivel"]
        )