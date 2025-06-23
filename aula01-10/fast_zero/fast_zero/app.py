from fastapi import FastAPI

from fast_zero.routes import token, user

app = FastAPI()
app.include_router(token.router)
app.include_router(user.router)
