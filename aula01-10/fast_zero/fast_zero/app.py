from fastapi import FastAPI

from fast_zero.routes import todos, token, users

app = FastAPI()
app.include_router(token.router)
app.include_router(users.router)
app.include_router(todos.router)
