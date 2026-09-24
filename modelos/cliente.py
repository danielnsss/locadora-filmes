
class Cliente:
    def __init__(self, id, nome, telefone):
        if type(id) is not int or id <= 0:
            raise ValueError("O ID deve ser um inteiro positivo.")

        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("O nome não pode estar vazio.")

        if not isinstance(telefone, str) or not telefone.strip():
            raise ValueError("O telefone não pode estar vazio.")

        self.id = id
        self.nome = nome.strip()
        self.telefone = telefone.strip()

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(id=dados["id"], nome=dados["nome"], telefone=dados["telefone"])