from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message

app = FastAPI()


@app.get(path='/', status_code=200, response_model=Message)
def read_root():
    return {'message': 'aula01-02'}


@app.get('/html', response_class=HTMLResponse)
def read_html():
    return """
    <body>
        Teste de api com html!
    <body/>
    """
