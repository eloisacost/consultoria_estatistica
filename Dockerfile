
FROM python:3.13-slim


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY api.py .

COPY modelo_churn_logistic.pkl . 


CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]
