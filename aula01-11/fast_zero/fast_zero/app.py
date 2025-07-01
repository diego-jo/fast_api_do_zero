from fastapi import FastAPI

from fast_zero.auth import router as auth
from fast_zero.todo import router as todos
from fast_zero.user import router as users

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
