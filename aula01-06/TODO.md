- [x] leitura inicial aula 06
- [x] setar ambiente de desenvolvimento
    - instalar:
        - pipx: `pip install --user pipx` | `sudo apt install pipx`
            - `pipx ensurepath`: add pacotes do pipx ao $PATH
        - poetry: `pipx install poetry`
            - `pipx inject poetry poetry-plugin-shell` | `poetry self add poetry-plugin-shell`
        - python(via poetry): `poetry python install 3.13.3`
        - poetry add -D pytest pytest-cov ruff taskipy

- [x] criar projeto com fastapi
    - comandos:
        - `poetry new --flat fast_zero`
        - setar versão python do projeto: `poetry env use 3.13`
            - alterar pyproject.toml: `requires-python = ">=3.13, <4.0"`
        - instalar fastapi: `poetry install` && `poetry add fastapi[standard]`


- [x] criar primeira rota e primeiro teste
- [x] definir rotas CRUD users
- [x] criar schemas e modelos
- [x] criar testes unitarios crud
- [x] criar fixture basica e add aos testes
- [x] configurar banco de dados
  - [x] instalar:
    - `poetry add sqlalchemy alembic pydantic-settings`
- [x] configurar gerenciador de migrations
  - iniciar controle de migrations com alembic
    - `alembic init migrations`
  - gerar migrations
    - `alembic revision --autogenerate -m "create users table"`
  - aplicando migration
    - `alembic upgrade head` para migratin mais nova ou `alembic upgrade 'id migration'`
    para migration específica

- [ ] evoluir rotas para usar banco ao inves de lista

- [ ] evoluir testes para usar o banco de dados
- [ ] evoluir testes
- [ ] aula 06 mão na massa


- [ ] descobrir como listar venvs no vscode como no windows
