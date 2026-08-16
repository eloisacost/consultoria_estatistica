"""
API de previsão de Churn — Regressão Logística
------------------------------------------------
Recebe os dados brutos de um cliente (como vinham no CSV original,
antes de qualquer encoding) e devolve a previsão de churn.

Para rodar localmente:
    

Depois acesse a documentação interativa em:
    http://127.0.0.1:8000/docs
"""

from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="API de Previsão de Churn",
    description="Prevê se um cliente de internet vai cancelar o serviço (churn).",
    version="1.0.0",
)

# Carrega o modelo treinado (o .pkl precisa estar na mesma pasta da API)
modelo = joblib.load("modelo_churn_logistic.pkl")

# Ordem EXATA das colunas usadas no treino (X_treino.columns).
# Isso é crítico: o LogisticRegression foi ajustado com essas 28 colunas,
# nesta ordem. Se mandarmos colunas faltando, sobrando ou fora de ordem,
# a previsão sai errada (ou dá erro).

COLUNAS_MODELO = [
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "PaperlessBilling",
    "TotalCharges",
    "gender_Male",
    "MultipleLines_No phone service",
    "MultipleLines_Yes",
    "InternetService_Fiber optic",
    "InternetService_No",
    "OnlineSecurity_No internet service",
    "OnlineSecurity_Yes",
    "OnlineBackup_No internet service",
    "OnlineBackup_Yes",
    "DeviceProtection_No internet service",
    "DeviceProtection_Yes",
    "TechSupport_No internet service",
    "TechSupport_Yes",
    "StreamingTV_No internet service",
    "StreamingTV_Yes",
    "StreamingMovies_No internet service",
    "StreamingMovies_Yes",
    "Contract_One year",
    "Contract_Two year",
    "PaymentMethod_Electronic check",
    "PaymentMethod_Mailed check",
]


# ---------------------------------------------------------------------------
# Formato de entrada: os mesmos campos "crus" que existiam no train.csv/test.csv,
# antes de qualquer encoding. Usar Literal nos campos categóricos evita que
# alguém mande "MASCULINO" em vez de "Male" e quebre o pré-processamento.
# ---------------------------------------------------------------------------
class ClienteInput(BaseModel):
    gender: Literal["Male", "Female"]
    SeniorCitizen: Literal[0, 1]
    Partner: Literal["Yes", "No"]
    Dependents: Literal["Yes", "No"]
    tenure: int = Field(..., ge=0, description="Meses de contrato")
    PhoneService: Literal["Yes", "No"]
    MultipleLines: Literal["Yes", "No", "No phone service"]
    InternetService: Literal["DSL", "Fiber optic", "No"]
    OnlineSecurity: Literal["Yes", "No", "No internet service"]
    OnlineBackup: Literal["Yes", "No", "No internet service"]
    DeviceProtection: Literal["Yes", "No", "No internet service"]
    TechSupport: Literal["Yes", "No", "No internet service"]
    StreamingTV: Literal["Yes", "No", "No internet service"]
    StreamingMovies: Literal["Yes", "No", "No internet service"]
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: Literal["Yes", "No"]
    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]
    TotalCharges: float

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "Yes",
                "Dependents": "No",
                "tenure": 12,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "Yes",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "Yes",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "TotalCharges": 850.50,
            }
        }


class PrevisaoOutput(BaseModel):
    churn_previsto: Literal["Yes", "No"]
    probabilidade_churn: float


def preprocessar(cliente: ClienteInput) -> pd.DataFrame:
    """
    Reproduz, para 1 cliente, exatamente o mesmo pré-processamento
    aplicado no notebook (mapeamento binário + one-hot com drop_first).

    Aqui montamos as colunas na mão (em vez de usar pd.get_dummies numa
    linha só) porque get_dummies numa única linha não sabe quais outras
    categorias existem — ele só cria colunas para os valores presentes
    naquela linha, o que quebraria o alinhamento com COLUNAS_MODELO.
    """
    dados = cliente.model_dump()

    linha = {
        "SeniorCitizen": 1 if dados["SeniorCitizen"] == 1 else 0,
        "Partner": 1 if dados["Partner"] == "Yes" else 0,
        "Dependents": 1 if dados["Dependents"] == "Yes" else 0,
        "tenure": dados["tenure"],
        "PhoneService": 1 if dados["PhoneService"] == "Yes" else 0,
        "PaperlessBilling": 1 if dados["PaperlessBilling"] == "Yes" else 0,
        "TotalCharges": dados["TotalCharges"],
        "gender_Male": dados["gender"] == "Male",
        "MultipleLines_No phone service": dados["MultipleLines"] == "No phone service",
        "MultipleLines_Yes": dados["MultipleLines"] == "Yes",
        "InternetService_Fiber optic": dados["InternetService"] == "Fiber optic",
        "InternetService_No": dados["InternetService"] == "No",
        "OnlineSecurity_No internet service": dados["OnlineSecurity"] == "No internet service",
        "OnlineSecurity_Yes": dados["OnlineSecurity"] == "Yes",
        "OnlineBackup_No internet service": dados["OnlineBackup"] == "No internet service",
        "OnlineBackup_Yes": dados["OnlineBackup"] == "Yes",
        "DeviceProtection_No internet service": dados["DeviceProtection"] == "No internet service",
        "DeviceProtection_Yes": dados["DeviceProtection"] == "Yes",
        "TechSupport_No internet service": dados["TechSupport"] == "No internet service",
        "TechSupport_Yes": dados["TechSupport"] == "Yes",
        "StreamingTV_No internet service": dados["StreamingTV"] == "No internet service",
        "StreamingTV_Yes": dados["StreamingTV"] == "Yes",
        "StreamingMovies_No internet service": dados["StreamingMovies"] == "No internet service",
        "StreamingMovies_Yes": dados["StreamingMovies"] == "Yes",
        "Contract_One year": dados["Contract"] == "One year",
        "Contract_Two year": dados["Contract"] == "Two year",
        "PaymentMethod_Electronic check": dados["PaymentMethod"] == "Electronic check",
        "PaymentMethod_Mailed check": dados["PaymentMethod"] == "Mailed check",
    }

    df = pd.DataFrame([linha])
    # Garante a mesma ordem de colunas do treino
    df = df[COLUNAS_MODELO]
    return df


@app.get("/")
def raiz():
    return {"status": "ok", "mensagem": "API de previsão de Churn no ar."}


@app.post("/predict", response_model=PrevisaoOutput)
def prever_churn(cliente: ClienteInput):
    try:
        X = preprocessar(cliente)
        pred = modelo.predict(X)[0]
        proba = modelo.predict_proba(X)[0][1]  # probabilidade da classe "1" (churn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar previsão: {e}")

    return PrevisaoOutput(
        churn_previsto="Yes" if pred == 1 else "No",
        probabilidade_churn=round(float(proba*100), 2),
    )



