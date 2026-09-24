import math

class Aluguel:
    def __init__(self, id, filme_id, cliente_id, data_aluguel, data_devolucao_prevista, valor_total, status="ativo", data_devolucao_real=None):
        if type(id) is not int or id <= 0:
            raise ValueError("O ID deve ser um inteiro positivo.")

        if type(filme_id) is not int or filme_id <= 0:
            raise ValueError("O ID do filme deve ser um inteiro positivo.")

        if type(cliente_id) is not int or cliente_id <= 0:
            raise ValueError("O ID do cliente deve ser um inteiro positivo.")

        if not isinstance(data_aluguel, str) or not data_aluguel.strip():
            raise ValueError("A data do aluguel não pode estar vazia.")

        if not isinstance(data_devolucao_prevista, str) or not data_devolucao_prevista.strip():
            raise ValueError("A data prevista para devolução não pode estar vazia.")

        if type(valor_total) not in (int, float) or not math.isfinite(valor_total) or valor_total < 0:
            raise ValueError("O valor total é inválido.")

        if status not in ("ativo", "devolvido"):
            raise ValueError("O status do aluguel é inválido.")

        if data_devolucao_real is not None and not isinstance(data_devolucao_real, str):
            raise ValueError("A data real de devolução deve ser um texto ou None.")

        if status == "ativo" and data_devolucao_real is not None:
            raise ValueError("Um aluguel ativo não pode possuir data real de devolução.")

        if status == "devolvido" and (data_devolucao_real is None or not data_devolucao_real.strip()):
            raise ValueError("Um aluguel devolvido deve possuir data real de devolução.")

        self.id = id
        self.filme_id = filme_id
        self.cliente_id = cliente_id
        self.data_aluguel = data_aluguel.strip()
        self.data_devolucao_prevista = data_devolucao_prevista.strip()
        self.data_devolucao_real = data_devolucao_real.strip() if data_devolucao_real is not None else None
        self.valor_total = float(valor_total)
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "filme_id": self.filme_id,
            "cliente_id": self.cliente_id,
            "data_aluguel": self.data_aluguel,
            "data_devolucao_prevista": self.data_devolucao_prevista,
            "data_devolucao_real": self.data_devolucao_real,
            "valor_total": self.valor_total,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(id=dados["id"], filme_id=dados["filme_id"], cliente_id=dados["cliente_id"], data_aluguel=dados["data_aluguel"], data_devolucao_prevista=dados["data_devolucao_prevista"], valor_total=dados["valor_total"], status=dados["status"], data_devolucao_real=dados["data_devolucao_real"])