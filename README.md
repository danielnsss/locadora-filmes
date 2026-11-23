# Locadora de Filmes — Trabalho 03 de POO II

Sistema de locadora de filmes desenvolvido em Python, com interface gráfica **PySide6**, API REST **FastAPI** e persistência em **PostgreSQL**, utilizando **SQLAlchemy**. A API e o banco são executados com **Docker Compose**; a interface gráfica é executada no computador cliente e se comunica com a API por HTTP.

## 1. Funcionalidades

- Cadastro, listagem, pesquisa e exclusão de filmes.
- Cadastro, consulta e exclusão de clientes.
- Registro de aluguéis com atualização da quantidade de exemplares disponíveis.
- Devolução de filmes e consulta ao histórico de aluguéis.
- Validações de dados e restrições para preservar a integridade dos registros.
- Acesso ao mesmo banco de dados por clientes em computadores diferentes, por meio da API.

## 2. Tecnologias e requisitos

**Servidor:** Docker Desktop com Docker Compose. O `Dockerfile.api` usa Python 3.12; o `compose.yaml` utiliza PostgreSQL 17 (imagem `postgres:17-alpine`).

**Cliente:** Python com suporte ao `PySide6==6.11.2` e ao `requests`. A versão **Python 3.14** foi utilizada no cliente durante os testes do projeto. Os comandos abaixo foram preparados para **Windows / PowerShell**.

Em uma instalação com dois computadores, ambos precisam estar na mesma rede e o servidor deve permitir conexões à porta TCP **8000**.

## 3. Organização do código

```text
codigo/
├── api/                         # Aplicação FastAPI, esquemas e rotas
├── banco/                       # Conexão, modelos SQLAlchemy e repositórios
├── interfaces/                  # Janelas PySide6 e tarefas de carregamento
├── modelos/                     # Classes de domínio
├── servicos/                    # Cliente HTTP da API (LocadoraRemota)
├── tests/                       # Testes automatizados
├── main.py                      # Ponto de entrada da interface
├── compose.yaml                 # Serviços PostgreSQL e FastAPI
├── Dockerfile.api               # Imagem do servidor
├── requirements-cliente.txt     # Dependências do cliente
├── requirements-servidor.txt    # Dependências do servidor
├── .env.example                 # Modelo de variáveis de ambiente
└── README.md
```

O relatório acadêmico encontra-se na pasta `relatorio/` do pacote de entrega.

## 4. Iniciar o servidor (PC 1)

Abra o **Docker Desktop** e aguarde a inicialização do mecanismo Docker. Em seguida, abra o PowerShell na pasta `codigo/`, onde está o arquivo `compose.yaml`.

### 4.1. Configurar as variáveis de ambiente

Na primeira instalação:

```powershell
Copy-Item .env.example .env
notepad .env
```

No arquivo `.env`, defina uma senha própria no campo `POSTGRES_PASSWORD`. As variáveis necessárias são:

```dotenv
POSTGRES_USER=locadora
POSTGRES_PASSWORD=DEFINA_UMA_SENHA_FORTE
POSTGRES_DB=locadora
API_HOST_BIND=127.0.0.1
```

- `API_HOST_BIND=127.0.0.1`: permite acesso à API somente pelo próprio PC servidor.
- `API_HOST_BIND=0.0.0.0`: permite acesso pela rede local, desde que o firewall e a rede autorizem. **Use essa opção apenas em rede confiável.**

**Não compartilhe nem inclua o arquivo `.env` no ZIP de entrega**; envie apenas `.env.example`.

### 4.2. Subir os contêineres

No PowerShell, dentro de `codigo/`:

```powershell
docker compose up -d --build
```

Verifique os serviços:

```powershell
docker compose ps
```

O serviço `db` deverá aparecer como `healthy`, e o serviço `api` como `Up`.

### 4.3. Conferir a API

No navegador do PC servidor, acesse:

- Documentação interativa: http://localhost:8000/docs
- Verificação da API e do banco: http://localhost:8000/saude

A rota `/saude` deve retornar `status: ok` e `banco: conectado` quando o acesso ao PostgreSQL estiver funcionando.

## 5. Executar a interface gráfica (PC 2 ou no próprio servidor)

Abra o PowerShell na pasta `codigo/` do computador onde a interface será executada.

### 5.1. Criar e ativar um ambiente virtual

Com Python 3.14 instalado:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-cliente.txt
```

Se o ambiente virtual já estiver configurado, basta ativá-lo; não é necessário criá-lo outra vez.

### 5.2. Definir o endereço da API

**Cliente no mesmo computador do servidor:**

```powershell
$env:API_BASE_URL = "http://127.0.0.1:8000"
```

**Cliente em outro computador da mesma rede:**

1. No PC servidor, descubra o endereço IPv4 da conexão Wi-Fi ou Ethernet (por exemplo, usando `& "$env:WINDIR\System32\ipconfig.exe"` no PowerShell).
2. No `.env` do **PC servidor**, configure `API_HOST_BIND=0.0.0.0`, se ainda não estiver assim, e aplique a configuração com `docker compose up -d`.
3. No **PC cliente**, informe o IPv4 *atual* do PC servidor:

```powershell
$env:API_BASE_URL = "http://IP_DO_SERVIDOR:8000"
```

Substitua `IP_DO_SERVIDOR` pelo endereço real, por exemplo `10.180.44.164`. Esse endereço é apenas ilustrativo e pode mudar ao trocar de rede.

O endereço da API é definido na sessão atual do PowerShell e precisa ser configurado novamente em uma nova sessão, se necessário.

### 5.3. Testar conexão e abrir a aplicação

No PC cliente:

```powershell
Test-NetConnection IP_DO_SERVIDOR -Port 8000
```

O campo `TcpTestSucceeded` deverá ser `True` (substitua `IP_DO_SERVIDOR` pelo IPv4 real). Em seguida:

```powershell
python main.py
```

A interface será aberta e usará os dados centralizados no PostgreSQL do servidor.

## 6. Executar os testes automatizados

O projeto contém **57 testes**: **47** testes de modelos, interfaces e histórico e **10** testes de integração da API, transações e concorrência.

### 6.1. Testes de modelos e interface (no ambiente do cliente)

Na pasta `codigo/`, com o `.venv` ativado e as dependências do cliente instaladas:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Resultado esperado para a versão entregue: `Ran 47 tests` e `OK`.

### 6.2. Testes de integração (no ambiente do servidor)

**Atenção:** os testes de integração exigem um banco separado, chamado `locadora_testes`. Eles possuem uma proteção para evitar sua execução no banco principal `locadora`.

Se o banco de testes ainda não existir, crie-o no contêiner PostgreSQL (substitua `locadora` pelo valor de `POSTGRES_USER` se tiver escolhido outro usuário):

```powershell
docker compose exec db createdb -U locadora locadora_testes
```

Se o banco já existir, pule a criação. Depois execute:

```powershell
docker compose exec -e POSTGRES_DB=locadora_testes api python -m unittest discover -s tests -p "integracao_*.py" -v
```

Resultado esperado: `Ran 10 tests` e `OK`. Não use o banco de produção para esses testes.

## 7. Comandos úteis e solução de problemas

**Visualizar serviços:**

```powershell
docker compose ps
```

**Consultar registros da API:**

```powershell
docker compose logs --tail=100 api
```

**Parar os contêineres sem apagar os dados armazenados:**

```powershell
docker compose down
```

**Falha de conexão entre os computadores:** verifique se estão na mesma rede, se o endereço IPv4 está atualizado, se `API_HOST_BIND=0.0.0.0` está configurado no servidor, se a API aparece como `Up` e se a porta 8000 é permitida pelo firewall do Windows.

**Não execute `docker compose down -v` durante a utilização normal:** a opção `-v` remove o volume Docker utilizado para persistir o banco de dados.

## 8. Observações para a entrega

O pacote deve incluir o **código-fonte**, os arquivos de configuração necessários, os **testes automatizados**, o **README.md** e o **relatório acadêmico em PDF**. Não inclua `.env` com credenciais, `.venv/`, arquivos `.pyc` ou pastas `__pycache__/`.

O cliente utiliza a API REST para acessar os dados; a base PostgreSQL não precisa ser instalada diretamente nos computadores clientes.
