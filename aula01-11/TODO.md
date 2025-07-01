- [x] leitura inicial aula 11
- [x] setar ambiente de desenvolvimento
    - instalar:
        - pipx: `pip install --user pipx` | `sudo apt install pipx`
            - `pipx ensurepath`: add pacotes do pipx ao $PATH
        - poetry: `pipx install poetry`
            - `pipx inject poetry poetry-plugin-shell` | `poetry self add poetry-plugin-shell`
        - python(via poetry): `poetry python install 3.13.3`

- [x] criar projeto com fastapi e configurar pyproject.toml
    - comandos:
        - `poetry new --flat fast_zero`
        - setar versão python do projeto: `poetry env use 3.13`
          - alterar pyproject.toml: `requires-python = ">=3.13, <4.0"`
        - `poetry add -D pytest pytest-asyncio pytest-cov ruff taskipy ipdb`
          - [x] instala das libs factory-boy e freezegun
        - `poetry add -D factory-boy freezegun`
        - configurar pyproject.toml
          - pytest
          - coverage
          - taskipy
          - ruff
        - instalar fastapi: `poetry install` && `poetry add 'fastapi[standard]`


- [x] instalar dependencias banco de dados já assincrono
    - `poetry add 'sqlalchemy[asyncio]' aiosqlite alembic pydantic-settings`

- [x] configurar gerenciador de variaveis de ambiente `settings.py`


- [x] definição de contratos API(schemas) e modelos de dados
  - [x] schemas (user, todo, security, filters(query_params default), filters(todos))
  - [x] models (user, todo)

- [x] configurar gerenciador de migrations
  - [x] iniciar controle de migrations com alembic
    - `alembic init migrations`
    - [x] configurar arquivo `migrations/env.py` com dados da base e models async
      - quebrar função `run_migrations_online` em 3 partes:
        - `run_migrations_online` -> iniciar execucao com `asyncio.run`
        - `do_run_migrations` -> recebe `connection` e executa migrations
        - `run_async_migrations` -> cria conexão assincrona e executa função sincrona de migrations

  - [x] gerar migrations
    - `alembic revision --autogenerate -m "create users table"`
  - [x] aplicando migration
    - `alembic upgrade head` para migratin mais nova ou `alembic upgrade 'id migration'`
    para migration específica
  - [x] criar config com função `get_session`
  - [x] criar `conftest.py` com fixture de `session`
  - [x] criar teste de persistencia para validar DB


- [ ] criar feature de autenticação/autorização
  - [x] instalar libs para autenticação/autorização
    - `poetry add pyjwt "pwdlib[argon2]"`
  - [x] criar modulo `security` com as funcionalidades abaixo:
    - [x] encripta password
    - [x] valida password
    - [x] gera encoded token
    - [x] funcao de extrair/validar informações token
    - [x] criar testes para funções do modulo `security.py`
  - [x] criar rota para gerar token
      - [x] implementar lógica da rota /token
    - [x] criar testes para rota /token
  - [x] criar rota para refresh token
    - [x] criar testes para rota refresh token

- [x] definir rotas CRUD `users`
- [x] proteger rotas de PUT, DELETE e GET by id
- [x] implementar lógica de todas as rotas CRUD considerando autenticação e autorização
- [x] criar fixture client, token para add aos testes
- [x] criar testes unitarios crud


- [x] definir rotas CRUD `todos`
- [ ] implementar lógica de todas as rotas CRUD considerando autorização
- [ ] criar fixtures necessárias para os testes
- [ ] criar testes para todas as operações de tarefas


- [ ] aula 11 docker e postgresql mão na massa
