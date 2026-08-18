from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Minha primeira API")


class Aluno(BaseModel):
    nome: str
    nota: float


@app.get("/")
async def inicio():
    return {"mensagem": "API no ar"}


@app.get(
    "/media",
    summary="Calcula média de duas notas",
    description="Recebe duas notas por query string e devolve a média.",
    tags=["Cálculos"]
)
async def calcular_media(n1: float, n2: float):
    media = (n1 + n2) / 2
    return {"n1": n1, "n2": n2, "media": media}


@app.post(
    "/avaliar",
    summary="Classifica o aluno por nota",
    description="Recebe nome e nota em JSON e informa aprovado ou reprovado.",
    tags=["Avaliação"],
    status_code=201
)
async def avaliar_aluno(aluno: Aluno):
    situacao = "aprovado" if aluno.nota >= 7 else "reprovado"
    return {
        "nome": aluno.nome,
        "nota": aluno.nota,
        "situacao": situacao
    }