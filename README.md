# Locadora de Filmes

Projeto da disciplina de Programação Orientada a Objetos II (POO II), desenvolvido em Python com a biblioteca PySide6.

O objetivo é construir uma aplicação desktop para gerenciamento de uma locadora de filmes, contemplando cadastro de filmes e clientes, consulta ao catálogo, aluguel, devolução e histórico de locações.

Os dados serão armazenados localmente em arquivos JSON.

> **Observação:** este documento define os contratos de integração entre os módulos do projeto. Qualquer alteração em atributos, assinaturas de métodos, formatos JSON ou sinais das interfaces deverá ser comunicada aos demais integrantes e registrada neste README antes da implementação.

## 1. Tecnologias utilizadas

- Python 3.14
- PySide6
- JSON
- Git e GitHub
- Visual Studio Code

As versões exatas das dependências Python utilizadas pelo projeto deverão ser registradas no arquivo `requirements.txt`.

## 2. Estrutura do projeto

```text
locadora_filmes/
│
├── main.py
│
├── modelos/
│   ├── __init__.py
│   ├── filme.py
│   ├── cliente.py
│   └── aluguel.py
│
├── servicos/
│   ├── __init__.py
│   └── locadora.py
│
├── armazenamento/
│   ├── __init__.py
│   └── json_repository.py
│
├── interfaces/
│   ├── __init__.py
│   ├── janela_principal.py
│   ├── janela_aluguel.py
│   └── janela_cadastro.py
│
├── dados/
│   ├── filmes.json
│   ├── clientes.json
│   └── alugueis.json
│
├── tests/
│   ├── test_modelos.py
│   ├── test_json_repository.py
│   └── test_locadora.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

## 3. Contratos dos modelos

Os contratos determinam os nomes dos atributos, seus tipos, os construtores, a serialização e as responsabilidades das classes.

Todos os integrantes deverão respeitar essas definições para garantir a compatibilidade entre os módulos.

### 3.1. Classe Filme

Arquivo: `modelos/filme.py`

Construtor:

```python
Filme(
    id,
    titulo,
    genero,
    ano,
    sinopse,
    preco_diaria,
    quantidade_total,
    quantidade_disponivel=None
)
```

Quando `quantidade_disponivel` não for informada, deverá assumir inicialmente o mesmo valor de `quantidade_total`.

| Atributo | Tipo | Descrição |
|---|---|---|
| id | int | Identificador único do filme. |
| titulo | str | Título do filme. |
| genero | str | Gênero cinematográfico. |
| ano | int | Ano de lançamento. |
| sinopse | str | Descrição do filme. |
| preco_diaria | float | Preço de uma diária de aluguel. |
| quantidade_total | int | Quantidade total de exemplares. |
| quantidade_disponivel | int | Exemplares disponíveis para aluguel. |

Regras:

- O identificador deve ser único.
- O título não pode estar vazio.
- O gênero não pode estar vazio.
- O ano deve ser um inteiro válido.
- O preço da diária deve ser maior ou igual a zero.
- A quantidade total deve ser maior ou igual a zero.
- A quantidade disponível deve estar entre zero e a quantidade total.
- A quantidade disponível diminui quando um exemplar é alugado e aumenta quando ele é devolvido.

Métodos de serialização:

```python
to_dict()
from_dict(dados)
```

- `to_dict()` retorna um dicionário compatível com `filmes.json`.
- `from_dict(dados)` cria um objeto `Filme` a partir de um dicionário.

### 3.2. Classe Cliente

Arquivo: `modelos/cliente.py`

Construtor:

```python
Cliente(id, nome, telefone)
```

| Atributo | Tipo | Descrição |
|---|---|---|
| id | int | Identificador único do cliente. |
| nome | str | Nome completo do cliente. |
| telefone | str | Telefone de contato. |

Regras:

- Cada cliente possui um identificador único.
- O nome é obrigatório.
- O telefone é obrigatório.
- Um cliente pode possuir vários aluguéis.

Métodos de serialização:

```python
to_dict()
from_dict(dados)
```

### 3.3. Classe Aluguel

Arquivo: `modelos/aluguel.py`

Construtor:

```python
Aluguel(id, filme_id, cliente_id, data_aluguel, data_devolucao_prevista, valor_total, status="ativo", data_devolucao_real=None)
```

| Atributo | Tipo | Descrição |
|---|---|---|
| id | int | Identificador único do aluguel. |
| filme_id | int | Identificador do filme alugado. |
| cliente_id | int | Identificador do cliente responsável. |
| data_aluguel | str | Data em que o aluguel foi realizado. |
| data_devolucao_prevista | str | Data prevista para devolução. |
| data_devolucao_real | str ou None | Data em que o filme foi devolvido. |
| valor_total | float | Valor total do aluguel. |
| status | str | Situação do aluguel. |

Os valores permitidos para `status` são:

- `ativo`: aluguel ainda não devolvido.
- `devolvido`: aluguel finalizado.

As datas deverão utilizar o formato `AAAA-MM-DD` e representar datas reais. A data prevista deverá ser posterior à data do aluguel; a data real da devolução não poderá ser anterior à data do aluguel (mas poderá ser anterior ou posterior à data prevista).

Enquanto o aluguel estiver ativo, `data_devolucao_real` deverá ser `None`.

Métodos de serialização:

```python
to_dict()
from_dict(dados)
```

## 4. Contratos do armazenamento JSON

Arquivo: `armazenamento/json_repository.py`

A classe `JSONRepository` será responsável exclusivamente pelo acesso aos arquivos JSON.

Construtor:

```python
JSONRepository(diretorio_dados=None)
```

Comportamento:

- Quando `diretorio_dados` for `None`, o repositório deverá utilizar a pasta `dados` existente na raiz do projeto.
- Quando um diretório for informado, deverá utilizá-lo. Isso permitirá o uso de pastas temporárias durante os testes.
- O repositório não deverá depender do diretório atual do terminal.
- Caminhos absolutos específicos do computador de um integrante não poderão ser utilizados.

Métodos:

```python
listar(tipo)
salvar(tipo, registros)
proximo_id(tipo)
```

O parâmetro `tipo` aceita somente:

- `filmes`
- `clientes`
- `alugueis`

O método `listar()` retorna uma lista de dicionários.

O método `salvar()` recebe uma lista de dicionários e grava os registros no arquivo correspondente. Tanto `listar()` quanto `salvar()` deverão exigir todos e somente os campos definidos pelos modelos e validar os valores por meio de `Filme.from_dict()`, `Cliente.from_dict()` ou `Aluguel.from_dict()`. Registros incompletos, com campos extras ou valores inválidos serão rejeitados com `ValueError`.

O método `proximo_id()` retorna um identificador inteiro ainda não utilizado. O identificador deverá ser calculado como:

```text
maior ID existente + 1
```

Quando a coleção estiver vazia, o primeiro identificador deverá ser `1`.

Todos os arquivos JSON terão uma lista como estrutura principal.

### 4.1. filmes.json

Exemplo:

```json
[
  {
    "id": 1,
    "titulo": "Interestelar",
    "genero": "Ficção científica",
    "ano": 2014,
    "sinopse": "Uma equipe de exploradores viaja pelo espaço.",
    "preco_diaria": 5.0,
    "quantidade_total": 3,
    "quantidade_disponivel": 2
  }
]
```

### 4.2. clientes.json

Exemplo com dados fictícios:

```json
[
  {
    "id": 1,
    "nome": "Cliente Exemplo",
    "telefone": "00000000000"
  }
]
```

### 4.3. alugueis.json

Exemplo:

```json
[
  {
    "id": 1,
    "filme_id": 1,
    "cliente_id": 1,
    "data_aluguel": "2026-09-22",
    "data_devolucao_prevista": "2026-09-25",
    "data_devolucao_real": null,
    "valor_total": 15.0,
    "status": "ativo"
  }
]
```

Os exemplos representam um aluguel ativo de um dos três exemplares do filme.

### 4.4. Regras de armazenamento

- Utilizar exatamente os nomes dos atributos definidos neste documento.
- Criar arquivos inexistentes com uma lista vazia (`[]`).
- Utilizar UTF-8 para leitura e gravação.
- Preservar acentos e caracteres especiais.
- Não utilizar caminhos absolutos específicos de um computador.
- Não apagar nem sobrescrever silenciosamente um arquivo quando ocorrer erro de leitura.
- Realizar a escrita primeiro em um arquivo temporário e substituir o arquivo original somente após a gravação bem-sucedida.
- Tratar erros de leitura, escrita, formatação JSON e estrutura inválida dos registros.
- Durante testes automatizados, utilizar diretórios temporários em vez da pasta real `dados`.
- Antes de operações que alterem mais de um arquivo, o serviço deverá manter os dados anteriores em memória e restaurá-los caso uma das gravações falhe.
- A aplicação não deverá ser utilizada simultaneamente em duas instâncias modificando os mesmos arquivos JSON.

### 4.5. Consistência entre arquivos

As operações de aluguel e devolução alteram mais de uma coleção.

No aluguel:

1. `alugueis.json` recebe um novo aluguel.
2. `filmes.json` reduz a quantidade disponível.

Na devolução:

1. `alugueis.json` atualiza o aluguel.
2. `filmes.json` aumenta a quantidade disponível.

O serviço `Locadora` será responsável por coordenar essas alterações. Caso uma gravação falhe, deverá tentar restaurar os dados anteriores, evitando que o estoque e os registros de aluguel permaneçam inconsistentes.

## 5. Contratos do serviço Locadora

Arquivo: `servicos/locadora.py`

A classe `Locadora` será responsável pelas regras de negócio da aplicação.

Todas as operações executadas pelas interfaces deverão passar por essa classe.

Construtor:

```python
Locadora(repositorio=None)
```

Comportamento:

- Quando `repositorio` for `None`, a classe deverá criar um `JSONRepository` utilizando a pasta padrão `dados`.
- Durante os testes, poderá receber um `JSONRepository` configurado com um diretório temporário.

### Métodos públicos obrigatórios

```python
listar_filmes()

obter_filme(filme_id)

buscar_filmes(termo)

cadastrar_filme(titulo, genero, ano, sinopse, preco_diaria, quantidade_total)

cadastrar_cliente(nome, telefone)

listar_clientes()

alugar_filme(filme_id, cliente_id, dias)

devolver_filme(aluguel_id)

listar_alugueis(status=None)
```

### Tipos de retorno

- `listar_filmes()`: lista de objetos `Filme`.
- `obter_filme()`: objeto `Filme`.
- `buscar_filmes()`: lista de objetos `Filme`.
- `cadastrar_filme()`: objeto `Filme` criado.
- `cadastrar_cliente()`: objeto `Cliente` criado.
- `listar_clientes()`: lista de objetos `Cliente`.
- `alugar_filme()`: objeto `Aluguel` criado.
- `devolver_filme()`: objeto `Aluguel` atualizado.
- `listar_alugueis()`: lista de objetos `Aluguel`.

### Regras de busca

`buscar_filmes(termo)` deverá pesquisar pelo título do filme, ignorando diferenças entre letras maiúsculas e minúsculas.

Quando `termo` estiver vazio, poderá retornar todos os filmes.

### Regras de cadastro de filme

1. Validar título e gênero.
2. Validar o ano.
3. Validar o preço da diária.
4. Validar a quantidade total.
5. Obter o próximo identificador.
6. Criar o objeto `Filme`.
7. Inicializar `quantidade_disponivel` com o mesmo valor de `quantidade_total`.
8. Persistir o filme.
9. Retornar o objeto criado.

### Regras de cadastro de cliente

1. Validar nome e telefone.
2. Obter o próximo identificador.
3. Criar o objeto `Cliente`.
4. Persistir o cliente.
5. Retornar o objeto criado.

### Regras de aluguel

1. Verificar se o filme existe.
2. Verificar se o cliente existe.
3. Verificar se existe pelo menos um exemplar disponível.
4. Validar se a quantidade de dias é um inteiro positivo.
5. Registrar a data atual como `data_aluguel`.
6. Calcular `data_devolucao_prevista` adicionando a quantidade de dias à data do aluguel.
7. Calcular o valor do aluguel multiplicando o preço da diária pela quantidade de dias.
8. Arredondar o valor total para duas casas decimais.
9. Registrar o aluguel com o status `ativo`.
10. Diminuir em uma unidade a quantidade disponível do filme.
11. Persistir as alterações de forma coordenada.
12. Retornar o objeto `Aluguel` criado.

### Regras de devolução

1. Verificar se o aluguel existe.
2. Verificar se seu status é `ativo`.
3. Verificar se o filme relacionado ao aluguel ainda existe.
4. Registrar a data atual como data real da devolução.
5. Alterar o status para `devolvido`.
6. Aumentar em uma unidade a disponibilidade do filme correspondente.
7. Garantir que `quantidade_disponivel` não ultrapasse `quantidade_total`.
8. Persistir as alterações de forma coordenada.
9. Retornar o objeto `Aluguel` atualizado.

Um aluguel já devolvido não poderá ser devolvido novamente.

### Tratamento de erros

Os métodos de negócio deverão sinalizar erros por meio de exceções.

Padrão adotado:

- `ValueError`: dados inválidos ou operação não permitida.
- `LookupError`: filme, cliente ou aluguel inexistente.
- `OSError`: falhas de leitura ou gravação que não puderem ser recuperadas pelo armazenamento.

As interfaces deverão capturar essas exceções e apresentar mensagens adequadas ao usuário por meio de diálogos do PySide6.

## 6. Contratos das interfaces

Todas as interfaces gráficas serão desenvolvidas utilizando PySide6.

As janelas não poderão modificar diretamente os arquivos JSON.

### 6.1. JanelaPrincipal

Arquivo: `interfaces/janela_principal.py`

Classe-base:

```python
QMainWindow
```

Construtor:

```python
JanelaPrincipal(locadora)
```

Responsabilidades:

- Exibir o catálogo de filmes.
- Permitir a pesquisa de filmes.
- Disponibilizar acesso ao cadastro.
- Abrir a janela de aluguel.
- Exibir os aluguéis ativos e/ou histórico.
- Permitir iniciar uma devolução.
- Atualizar as informações após cadastros, aluguéis e devoluções.
- Exibir menu e barra de ferramentas.
- Implementar tratamento do evento de fechamento da aplicação.
- Permitir a abertura de um filme por duplo clique ou ação equivalente.

### 6.2. JanelaAluguel

Arquivo: `interfaces/janela_aluguel.py`

Classe-base:

```python
QDialog
```

Construtor:

```python
JanelaAluguel(locadora, filme_id)
```

Sinal:

```python
aluguel_realizado = Signal()
```

Responsabilidades:

- Obter o filme por meio de `locadora.obter_filme(filme_id)`.
- Apresentar o filme selecionado.
- Permitir a seleção de um cliente.
- Receber a quantidade de dias.
- Exibir o valor total calculado.
- Confirmar o aluguel.
- Apresentar mensagens de sucesso ou erro.
- Emitir `aluguel_realizado` após uma locação concluída com sucesso.

### 6.3. JanelaCadastro

Arquivo: `interfaces/janela_cadastro.py`

Classe-base:

```python
QDialog
```

Construtor:

```python
JanelaCadastro(locadora)
```

Sinais:

```python
filme_cadastrado = Signal()
cliente_cadastrado = Signal()
```

Responsabilidades:

- Disponibilizar formulários para o cadastro de filmes e clientes.
- Validar campos obrigatórios antes de enviar a operação ao serviço.
- Enviar as informações ao serviço `Locadora`.
- Apresentar mensagens de confirmação e erro.
- Emitir o sinal correspondente após um cadastro concluído.

### 6.4. Compartilhamento do serviço

O arquivo `main.py` criará uma única instância de `Locadora`.

Essa instância será compartilhada com todas as janelas.

As interfaces deverão utilizar somente os métodos públicos do serviço e não acessar diretamente os arquivos JSON.

Exemplo conceitual:

```python
locadora = Locadora()
janela = JanelaPrincipal(locadora)
```

### 6.5. Comunicação entre janelas

A `JanelaPrincipal` deverá conectar-se aos sinais emitidos pelas janelas adicionais.

Exemplo:

```python
janela_aluguel.aluguel_realizado.connect(self.atualizar_catalogo)
janela_cadastro.filme_cadastrado.connect(self.atualizar_catalogo)
```

Isso evita que uma janela altere diretamente componentes internos de outra.

## 7. Conteúdos obrigatórios de PySide6

O projeto deverá demonstrar explicitamente os tópicos exigidos na atividade.

| Conteúdo | Implementação planejada |
|---|---|
| Sinais e slots | Cliques de botões, campo de pesquisa e sinais entre as janelas. |
| Eventos | `closeEvent()` na janela principal e evento de duplo clique em filme. |
| Diversos tipos de widgets | `QPushButton`, `QLineEdit`, `QTableWidget` ou equivalente, `QComboBox`, `QSpinBox`, `QDoubleSpinBox`, `QLabel`, entre outros. |
| Layouts | `QVBoxLayout`, `QHBoxLayout` e `QFormLayout`. |
| Barra de menu | `QMenuBar` na janela principal. |
| Barra de ferramentas | `QToolBar` na janela principal. |
| Dialogs/Alerts | `QDialog` nas janelas adicionais e `QMessageBox` para confirmações, erros e avisos. |
| Janela adicional | `JanelaAluguel` e `JanelaCadastro`. |

O relatório deverá identificar onde cada tópico foi utilizado.

## 8. Divisão das responsabilidades

### Integrante 1 — Modelos e armazenamento

Arquivos principais:

- `modelos/filme.py`
- `modelos/cliente.py`
- `modelos/aluguel.py`
- `armazenamento/json_repository.py`
- `dados/*.json`
- `tests/test_modelos.py`
- `tests/test_json_repository.py`

Responsável por:

- Implementação das classes.
- Validações básicas dos modelos.
- Serialização e desserialização.
- Persistência JSON.
- Geração dos identificadores.
- Testes de modelos e armazenamento.

### Integrante 2 — Serviço e aluguel

Arquivos principais:

- `servicos/locadora.py`
- `interfaces/janela_aluguel.py`
- `tests/test_locadora.py`

Responsável por:

- Regras de negócio.
- Cadastro por meio do serviço.
- Controle de disponibilidade.
- Aluguel.
- Devolução.
- Consistência entre os arquivos.
- Janela de aluguel.
- Testes das regras de negócio.

### Integrante 3 — Interface principal e cadastro

Arquivos principais:

- `main.py`
- `interfaces/janela_principal.py`
- `interfaces/janela_cadastro.py`

Responsável por:

- Inicialização da aplicação.
- Interface principal.
- Catálogo.
- Pesquisa.
- Menus e barra de ferramentas.
- Formulários de cadastro.
- Integração visual das janelas.
- Atualização da interface por sinais.

O relatório, o README, os testes finais de integração e a revisão da entrega serão responsabilidades compartilhadas.

## 9. Regras de integração com Git

Cada integrante deverá desenvolver suas funcionalidades em uma branch própria.

Branches:

```text
main
feat/modelos-json
feat/locacoes
feat/interface
```

A branch `main` deverá permanecer executável e conter apenas alterações já revisadas.

Antes de enviar alterações para a branch principal:

1. Atualizar a branch de trabalho com a versão mais recente da `main`.
2. Verificar se os métodos respeitam os contratos deste documento.
3. Executar os testes relacionados ao módulo.
4. Executar `python main.py` quando a alteração envolver integração com a interface.
5. Verificar se não foram adicionados arquivos temporários, `.venv`, `__pycache__` ou dados de teste.
6. Criar um Pull Request.
7. Solicitar revisão de outro integrante.
8. Resolver conflitos e executar novamente os testes.
9. Integrar somente após a verificação.

Qualquer alteração nos contratos deverá ser aprovada pelos demais integrantes e registrada neste documento antes da implementação.

### 9.1. Commits

Preferir commits pequenos e objetivos.

Exemplos:

```text
Implementa modelo Filme
Adiciona persistência JSON
Implementa aluguel de filmes
Cria janela de cadastro
Corrige atualização do estoque
```

Evitar commits genéricos como:

```text
alterações
teste
mudanças
final
```

## 10. Testes

Os testes automatizados deverão utilizar dados temporários, sem alterar os arquivos reais da pasta `dados`.

### 10.1. Testes dos modelos

- Criar objetos válidos.
- Converter objetos para dicionários.
- Reconstruir objetos por `from_dict()`.
- Rejeitar valores inválidos quando aplicável.

### 10.2. Testes do armazenamento

- Criar automaticamente arquivos inexistentes.
- Ler listas vazias.
- Salvar e recuperar registros.
- Calcular corretamente o próximo ID.
- Preservar caracteres acentuados.
- Testar comportamento com JSON inválido, registros incompletos, campos extras, datas inválidas e dados que violem os modelos.
- Verificar que uma falha de escrita não destrói o arquivo anterior.

### 10.3. Testes do serviço

- Cadastrar um filme.
- Cadastrar um cliente.
- Pesquisar um filme.
- Obter um filme por ID.
- Alugar um filme disponível.
- Tentar alugar um filme inexistente.
- Tentar alugar para um cliente inexistente.
- Tentar alugar um filme indisponível.
- Rejeitar quantidade de dias igual ou menor que zero.
- Consultar os aluguéis ativos.
- Devolver um filme.
- Tentar devolver novamente o mesmo aluguel.
- Confirmar a restauração da disponibilidade após a devolução.

### 10.4. Testes de integração

Os três integrantes deverão executar conjuntamente:

- Iniciar a aplicação.
- Cadastrar um filme.
- Cadastrar um cliente.
- Pesquisar o filme cadastrado.
- Realizar um aluguel.
- Verificar a atualização do estoque na interface e no JSON.
- Fechar e reabrir a aplicação.
- Verificar a permanência dos dados.
- Realizar a devolução.
- Verificar a atualização do histórico e do estoque.
- Confirmar o funcionamento dos menus, barra de ferramentas, sinais, eventos, diálogos e janelas adicionais.
- Executar o projeto em outro ambiente Python com as dependências do `requirements.txt`.

## 11. Como configurar e executar

### 11.1. Criar o ambiente virtual

No Windows:

```powershell
py -3.14 -m venv .venv
```

Caso o computador não utilize o Python Launcher (`py`), poderá ser usado:

```powershell
python -m venv .venv
```

### 11.2. Instalar as dependências

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 11.3. Executar a aplicação

```powershell
.\.venv\Scripts\python.exe main.py
```

### 11.4. Atualizar requirements.txt

Após instalar ou alterar uma dependência:

```powershell
.\.venv\Scripts\python.exe -m pip freeze > requirements.txt
```

## 12. Arquivo .gitignore

O arquivo `.gitignore` deverá conter, no mínimo:

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
.vscode/
```

Os arquivos reais de `dados/` fazem parte da aplicação e poderão permanecer no repositório com dados iniciais controlados pela equipe.

Dados criados exclusivamente para testes não deverão ser enviados.

## 13. Uso de IA generativa

Conforme a atividade, ferramentas de IA generativa deverão ser utilizadas somente como ferramenta de auxílio durante o desenvolvimento.

Quando utilizadas, o relatório deverá registrar:

- Qual ferramenta foi utilizada.
- Em qual etapa foi utilizada.
- Qual foi a finalidade do uso.
- Como a equipe revisou ou adaptou o resultado obtido.

A equipe é responsável por compreender, revisar, testar e integrar todo código utilizado no projeto.

## 14. Documentação

O relatório final deverá seguir o modelo de artigos da Sociedade Brasileira de Computação (SBC).

Deverá conter:

- Identificação dos integrantes.
- Descrição geral do projeto e da interface.
- Documentação de todos os widgets criados.
- Especificação das ferramentas de IA utilizadas, quando e por qual razão, caso tenham sido utilizadas.

Além disso, o relatório deverá relacionar os elementos da interface com os conteúdos obrigatórios de PySide6 implementados no projeto.

## 15. Critérios internos para considerar uma funcionalidade concluída

Uma funcionalidade somente será considerada pronta quando:

1. Respeitar os contratos definidos neste README.
2. Não alterar diretamente JSON a partir da interface.
3. Passar nos testes aplicáveis.
4. Não quebrar funcionalidades existentes.
5. Possuir tratamento adequado dos erros esperados.
6. Estiver integrada à versão mais recente da `main`.
7. Tiver sido revisada por pelo menos outro integrante.
