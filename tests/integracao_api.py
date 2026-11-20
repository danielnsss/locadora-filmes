import unittest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.dependencias import obter_sessao
from api.main import app
from banco.conexao import engine
from banco.modelos_db import Base


class TestIntegracaoAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if engine.url.database != "locadora_testes":
            raise RuntimeError("Os testes só podem usar o banco locadora_testes.")

        Base.metadata.create_all(bind=engine)

    def setUp(self):
        self.conexao = engine.connect()
        self.transacao = self.conexao.begin()
        self.sessao = Session(
            bind=self.conexao,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )

        def sessao_de_teste():
            yield self.sessao

        app.dependency_overrides[obter_sessao] = sessao_de_teste
        self.cliente_http = TestClient(app)

    def tearDown(self):
        self.cliente_http.close()
        app.dependency_overrides.pop(obter_sessao, None)
        self.sessao.close()
        self.transacao.rollback()
        self.conexao.close()

    def cadastrar_filme(self):
        resposta = self.cliente_http.post(
            "/filmes",
            json={
                "titulo": "Filme de integração",
                "genero": "Ficção científica",
                "ano": 2014,
                "sinopse": "Registro exclusivo de teste.",
                "preco_diaria": 7.0,
                "quantidade_total": 3,
            },
        )
        self.assertEqual(resposta.status_code, 201, resposta.text)
        return resposta.json()

    def cadastrar_cliente(self):
        resposta = self.cliente_http.post(
            "/clientes",
            json={"nome": "Cliente de integração", "telefone": "89999990001"},
        )
        self.assertEqual(resposta.status_code, 201, resposta.text)
        return resposta.json()

    def test_01_cadastrar_consultar_e_pesquisar_filme(self):
        filme = self.cadastrar_filme()

        consulta = self.cliente_http.get(f"/filmes/{filme['id']}")
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json()["titulo"], filme["titulo"])

        pesquisa = self.cliente_http.get("/filmes", params={"termo": "integração"})
        self.assertEqual(pesquisa.status_code, 200)
        self.assertTrue(any(item["id"] == filme["id"] for item in pesquisa.json()))

    def test_02_cadastrar_consultar_e_excluir_cliente(self):
        cliente = self.cadastrar_cliente()

        consulta = self.cliente_http.get(f"/clientes/{cliente['id']}")
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json()["nome"], cliente["nome"])

        exclusao = self.cliente_http.delete(f"/clientes/{cliente['id']}")
        self.assertEqual(exclusao.status_code, 204)
        self.assertEqual(
            self.cliente_http.get(f"/clientes/{cliente['id']}").status_code, 404
        )

    def test_03_aluguel_devolucao_e_integridade(self):
        filme = self.cadastrar_filme()
        cliente = self.cadastrar_cliente()
        filme_id = filme["id"]
        cliente_id = cliente["id"]

        resposta = self.cliente_http.post(
            "/alugueis",
            json={"filme_id": filme_id, "cliente_id": cliente_id, "dias": 3},
        )
        self.assertEqual(resposta.status_code, 201, resposta.text)
        aluguel = resposta.json()
        self.assertEqual(aluguel["status"], "ativo")
        self.assertEqual(aluguel["valor_total"], 21.0)

        estoque = self.cliente_http.get(f"/filmes/{filme_id}").json()
        self.assertEqual(estoque["quantidade_disponivel"], 2)
        self.assertEqual(self.cliente_http.delete(f"/filmes/{filme_id}").status_code, 409)
        self.assertEqual(self.cliente_http.delete(f"/clientes/{cliente_id}").status_code, 409)

        devolucao = self.cliente_http.patch(f"/alugueis/{aluguel['id']}/devolucao")
        self.assertEqual(devolucao.status_code, 200, devolucao.text)
        self.assertEqual(devolucao.json()["status"], "devolvido")
        self.assertIsNotNone(devolucao.json()["data_devolucao_real"])
        self.assertEqual(
            self.cliente_http.get(f"/filmes/{filme_id}").json()["quantidade_disponivel"], 3
        )
        self.assertEqual(
            self.cliente_http.patch(f"/alugueis/{aluguel['id']}/devolucao").status_code,
            409,
        )
        self.assertEqual(self.cliente_http.delete(f"/filmes/{filme_id}").status_code, 409)
        self.assertEqual(self.cliente_http.delete(f"/clientes/{cliente_id}").status_code, 409)

        historico = self.cliente_http.get("/alugueis", params={"status": "devolvido"})
        self.assertEqual(historico.status_code, 200)
        self.assertTrue(any(item["id"] == aluguel["id"] for item in historico.json()))

    def test_04_excluir_filme_sem_historico(self):
        filme = self.cadastrar_filme()
        exclusao = self.cliente_http.delete(f"/filmes/{filme['id']}")
        self.assertEqual(exclusao.status_code, 204)
        self.assertEqual(self.cliente_http.get(f"/filmes/{filme['id']}").status_code, 404)

    def test_05_rejeitar_dados_invalidos(self):
        resposta = self.cliente_http.post(
            "/alugueis", json={"filme_id": 0, "cliente_id": 1, "dias": 0}
        )
        self.assertEqual(resposta.status_code, 422)
        self.assertEqual(self.cliente_http.get("/filmes/0").status_code, 422)
        self.assertEqual(self.cliente_http.get("/alugueis", params={"status": "invalido"}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
