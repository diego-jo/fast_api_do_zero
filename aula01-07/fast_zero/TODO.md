- [x] leitura inicial aula 07
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


- [x] configurar banco de dados
  - [x] instalar:
    - `poetry add sqlalchemy alembic pydantic-settings`
  - [x] configurar gerenciador de variaveis de ambiente `settings.py`
- [x] configurar gerenciador de migrations
  - iniciar controle de migrations com alembic
    - `alembic init migrations`
  - gerar migrations
    - `alembic revision --autogenerate -m "create users table"`
  - aplicando migration
    - `alembic upgrade head` para migratin mais nova ou `alembic upgrade 'id migration'`
    para migration específica

- [x] definir rotas CRUD users
- [x] criar schemas e modelos
- [x] criar fixture client para add aos testes
- [x] criar testes unitarios crud
- [x] instalar libs para autenticação/autorização
  - `poetry add pyjwt "pwdlib[argon2]"`
- [ ] criar feature de autenticação/autorização
  - [ ] criar modulo `security` com as funcionalidades abaixo:
    - [x] encripta password
    - [x] valida password
    - [x] gera encoded token
    - [x] extrai/valida informações token
    - [x] criar rota para gerar token
    - [x] criar testes para rota token e funções do modulo `security.py`
    - [x] proteger rotas de put e delete
- [x] evoluir testes para autenticação/autorização

- [ ] aula 07 refatorar estrutura do projeto mão na massa
