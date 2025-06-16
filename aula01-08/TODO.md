- [x] leitura inicial aula 08
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
        - `poetry add -D pytest pytest-cov ruff taskipy`
        - configurar pyproject.toml
          - pytest
          - taskipy
          - ruff
        - instalar fastapi: `poetry install` && `poetry add 'fastapi[standard]`





- [x] instalar dependencias banco de dados
  - [x] instalar:
    - `poetry add sqlalchemy alembic pydantic-settings`

- [x] configurar gerenciador de variaveis de ambiente `settings.py`


- [x] definição de contratos API(schemas) e modelos de dados
  - [x] schemas (user, security, filters(query_params))
  - [x] models (user)

- [x] configurar gerenciador de migrations
  - [x] iniciar controle de migrations com alembic
    - `alembic init migrations`
    - configurar arquivo `migrations/env.py` com dados da base e models
  - [x] gerar migrations
    - `alembic revision --autogenerate -m "create users table"`
  - [x] aplicando migration
    - `alembic upgrade head` para migratin mais nova ou `alembic upgrade 'id migration'`
    para migration específica
  - [x] criar config com função `get_session`


- [x] criar feature de autenticação/autorização
  - [x] criar modulo `security` com as funcionalidades abaixo:
    - [x] encripta password
    - [x] valida password
    - [x] gera encoded token
    - [ ] funcao de extrair/validar informações token
  - [x] criar rota para gerar token
      - [x] implementar lógica da rota /token
    - [x] criar testes para rota /token e funções do modulo `security.py`
    - [x] alterar rotas create e update user para criptografar password antes de salvar
- [x] proteger rotas de PUT e DELETE
- [ ] evoluir testes para autenticação/autorização
  - [x] criar fixture de geração de token
  - [x] alterar testes para receber token

- [x] definir rotas CRUD users
  - [x] implementar lógica de todas as rotas CRUD
- [x] criar fixture client para add aos testes
- [x] criar testes unitarios crud

- [x] instalar libs para autenticação/autorização
  - `poetry add pyjwt "pwdlib[argon2]"`

- [ ] aula 08 tornar projeto assincrono mão na massa
