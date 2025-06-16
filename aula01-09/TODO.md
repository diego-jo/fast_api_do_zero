- [ ] leitura inicial aula 09
- [ ] setar ambiente de desenvolvimento
    - instalar:
        - pipx: `pip install --user pipx` | `sudo apt install pipx`
            - `pipx ensurepath`: add pacotes do pipx ao $PATH
        - poetry: `pipx install poetry`
            - `pipx inject poetry poetry-plugin-shell` | `poetry self add poetry-plugin-shell`
        - python(via poetry): `poetry python install 3.13.3`

- [ ] criar projeto com fastapi e configurar pyproject.toml
    - comandos:
        - `poetry new --flat fast_zero`
        - setar versão python do projeto: `poetry env use 3.13`
          - alterar pyproject.toml: `requires-python = ">=3.13, <4.0"`
        - `poetry add -D pytest pytest-cov ruff taskipy`
        - configurar pyproject.toml
          - pytest
          - taskipy
          - ruff
        - instalar fastapi: `poetry install` && `poetry add 'fastapi[standard]`


- [ ] instalar dependencias banco de dados
  - [ ] instalar:
    - `poetry add sqlalchemy alembic pydantic-settings`

- [ ] configurar gerenciador de variaveis de ambiente `settings.py`


- [ ] instalar libs necessárias para execução assincrona
  - `poetry add 'sqlalchemy[asyncio]' aiosqlite`
  - `poetry add -D pytest-asyncio`


- [ ] definição de contratos API(schemas) e modelos de dados  
  - [ ] schemas (user, security, filters(query_params))
  - [ ] models (user)

- [ ] configurar gerenciador de migrations
  - [ ] iniciar controle de migrations com alembic
    - `alembic init migrations`
    - configurar arquivo `migrations/env.py` asincrono com dados da base e models
  - [ ] gerar migrations
    - `alembic revision --autogenerate -m "create users table"`
  - [ ] aplicando migration
    - `alembic upgrade head` para migratin mais nova ou `alembic upgrade 'id migration'`
    para migration específica
  - [ ] criar config com função `get_session` asincrono


- [ ] instalar libs para autenticação/autorização
  - `poetry add pyjwt "pwdlib[argon2]"`

- [ ] criar feature de autenticação/autorização
  - [ ] criar modulo `security` com as funcionalidades abaixo:
    - [ ] encripta password
    - [ ] valida password
    - [ ] gera encoded token
    - [ ] funcao de extrair/validar informações token
  - [ ] criar rota para gerar token
      - [ ] implementar lógica da rota /token
    - [ ] criar testes para rota /token e funções do modulo `security.py`
    - [ ] alterar rotas create e update user para criptografar password antes de salvar
- [ ] proteger rotas de PUT e DELETE
- [ ] evoluir testes para autenticação/autorização
  - [ ] criar fixture de geração de token
  - [ ] alterar testes para receber token

- [ ] definir rotas CRUD users
  - [ ] implementar lógica de todas as rotas CRUD
- [ ] criar fixture client, token, session(asincrono) e mock_db_time para add aos testes
- [ ] criar testes unitarios crud
