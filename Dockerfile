# 1. Pega um computador zerado com Python instalado
FROM python:3.10-slim

# 2. Cria uma pasta chamada /app dentro do servidor
WORKDIR /app

# 3. Copia a lista de compras e instala as bibliotecas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o seu código da API e o seu modelo estatístico
COPY api.py .
# ATENÇÃO: Substitua 'modelo.pkl' pelo nome exato do arquivo do seu modelo treinado!
COPY modelo_churn_logistic.pkl . 

# 5. Avisa o servidor qual comando usar para ligar a API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]