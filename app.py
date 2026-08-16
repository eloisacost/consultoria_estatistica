"""
Interface Streamlit para a API de previsão de Churn.

Pré-requisito: a API (app.py) precisa estar rodando antes de usar esta tela:
    uvicorn api:app --reload

Para rodar esta interface:
    streamlit run app.py
"""


import requests
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Consultoria: Previsão de Churn", layout="wide") 


api_url = "http://127.0.0.1:8000/predict"

tab1, tab2, tab3, tab4 = st.tabs([
    "Sobre o modelo",
    "Previsão de Churn",
    "Simulador Estratégico",
    "Instruções"
])

with tab1:
    st.title("Sobre o modelo")
    st.write("""O modelo escolhido foi a **Regressão Logística**. Ele foi treinado com dados de clientes de uma empresa de telecomunicações, com o objetivo de prever o risco de cancelamento do serviço (*churn*) com base nas características dos clientes. A mesma abordagem pode ser aplicada a diferentes contextos de cancelamento de serviços, como o encerramento de uma assinatura de streaming ou de um contrato de telefonia móvel, utilizando dados previamente registrados sobre os clientes.

Para o treinamento, foram utilizados dados de clientes que cancelaram o serviço e de clientes que permaneceram ativos. Dessa forma, o modelo foi capaz de identificar padrões nas características dos clientes associados à ocorrência ou não do *churn*.

Durante o processo de preparação dos dados, as variáveis **"MonthlyCharges"** e **"PaymentMethod_Credit card (automatic)"** foram excluídas do treinamento. Além disso, foi aplicado o **teste de qui-quadrado de independência** para avaliar a relação entre as variáveis categóricas e a variável de interesse. As variáveis que não apresentaram significância estatística foram excluídas do modelo.

Após o processo de seleção das variáveis, o modelo foi treinado utilizando **28 variáveis**. Como resultado, apresentou **acurácia de 85,4%**, **F1-Score de 66,6%**, **precisão de 68,6%** e **Recall de 64,8%**.""")

with tab2:
    st.title("Previsão de Churn")
    st.write("Preencha os dados do cliente e clique em **Prever** para consultar a API do modelo de regressão logística.")

    with st.form("form_cliente"):
        st.subheader("Dados do cliente")

        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gênero", ["Female", "Male"])
            senior = st.selectbox("Idoso (SeniorCitizen)", [0, 1], format_func=lambda x: "Sim" if x == 1 else "Não")
            partner = st.selectbox("Possui parceiro(a)?", ["Yes", "No"])
            dependents = st.selectbox("Possui dependentes?", ["Yes", "No"])
            tenure = st.number_input("Tenure (meses de contrato)", min_value=0, max_value=100, value=12)
            phone_service = st.selectbox("Possui serviço de telefone?", ["Yes", "No"])
            multiple_lines = st.selectbox("Múltiplas linhas?", ["No", "Yes", "No phone service"])
            internet_service = st.selectbox("Serviço de internet", ["DSL", "Fiber optic", "No"])
            online_security = st.selectbox("Segurança online", ["No", "Yes", "No internet service"])

        with col2:
            online_backup = st.selectbox("Backup online", ["No", "Yes", "No internet service"])
            device_protection = st.selectbox("Proteção de dispositivo", ["No", "Yes", "No internet service"])
            tech_support = st.selectbox("Suporte técnico", ["No", "Yes", "No internet service"])
            streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
            streaming_movies = st.selectbox("Streaming Filmes", ["No", "Yes", "No internet service"])
            contract = st.selectbox("Tipo de contrato", ["Month-to-month", "One year", "Two year"])
            paperless_billing = st.selectbox("Fatura sem papel?", ["Yes", "No"])
            payment_method = st.selectbox(
                "Método de pagamento",
                ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
            )
            total_charges = st.number_input("Total gasto (TotalCharges)", min_value=0.0, value=850.50, step=10.0)

        enviar = st.form_submit_button("Analisar Risco")

    if enviar:
        payload = {
            "gender": gender, "SeniorCitizen": senior, "Partner": partner, "Dependents": dependents,
            "tenure": tenure, "PhoneService": phone_service, "MultipleLines": multiple_lines,
            "InternetService": internet_service, "OnlineSecurity": online_security,
            "OnlineBackup": online_backup, "DeviceProtection": device_protection,
            "TechSupport": tech_support, "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies, "Contract": contract,
            "PaperlessBilling": paperless_billing, "PaymentMethod": payment_method,
            "TotalCharges": total_charges,
        }

        try:
            with st.spinner("Consultando a API..."):
                resposta = requests.post(api_url, json=payload, timeout=10)
        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar à API. Confirme se ela está rodando em `uvicorn api:app --reload`.")
            st.stop()

        if resposta.status_code != 200:
            st.error(f"Erro da API ({resposta.status_code}): {resposta.text}")
            st.stop()

        resultado = resposta.json()
        churn = resultado["churn_previsto"]
        probabilidade = resultado["probabilidade_churn"]

        st.session_state['cliente_payload'] = payload
        st.session_state['cliente_prob'] = probabilidade
        st.session_state['cliente_total_charges'] = total_charges

        st.subheader("Resultado do Diagnóstico")
        
        # AQUI FOI A SUA MUDANÇA
        if churn == "Yes":
            st.error(f"Alerta: Risco de Churn Elevado — {probabilidade:.2f}% de chance de cancelamento.")
            st.progress(min(int(probabilidade), 100))
            st.info("**Ação Recomendada:** Acesse a aba **Simulador Estratégico** para avaliar cenários de retenção e viabilidade financeira.")
        else:
            st.success(f"Cliente Estável: Risco de Churn Baixo — {probabilidade:.2f}% de chance de cancelamento.")
            st.progress(min(int(probabilidade), 100))

with tab3:
    st.title("Simulador Estratégico e Viabilidade Financeira")
    st.write("Acompanhe o impacto de ofertas de retenção no comportamento do cliente e na receita da empresa.")

    if 'cliente_payload' not in st.session_state:
        st.warning("Nenhum cliente em análise. Volte na aba **Previsão de Churn** para carregar um perfil.")
    else:
        prob_atual = st.session_state['cliente_prob']
        payload_atual = st.session_state['cliente_payload']
        total_charges_atual = st.session_state['cliente_total_charges']

        st.subheader("1. Configurar Oferta de Retenção")
        
        col_sim1, col_sim2 = st.columns(2)
        
        with col_sim1:
            st.markdown("**Alavancas Financeiras e Contratuais**")
            desconto = st.slider("Desconto na Fatura (%)", 0, 50, 0, step=5)
            novo_contrato = st.selectbox("Alterar período de fidelidade para:", 
                                         ["Manter o mesmo", "One year"])
            
            st.markdown("**Armazenamento e Proteção**")
            add_backup = st.checkbox("Incluir Backup na Nuvem (Online Backup)")
            add_prot = st.checkbox("Incluir Proteção de Dispositivos")
            
        with col_sim2:
            st.markdown("**Melhorias de Serviço e Entretenimento**")
            st.caption("Selecione para conceder isenção em serviços adicionais:")
            add_tech = st.checkbox("Incluir Suporte Técnico Premium")
            add_sec = st.checkbox("Incluir Segurança Online Avançada")
            add_stream_tv = st.checkbox("Incluir Pacote de Streaming de TV")
            add_stream_mov = st.checkbox("Incluir Pacote de Streaming de Filmes")

        if st.button("Executar Simulação de Cenário", type="primary"):
            payload_sim = payload_atual.copy()
            
            valor_desconto_real = total_charges_atual * (desconto / 100.0)
            receita_projetada = total_charges_atual - valor_desconto_real
            payload_sim["TotalCharges"] = receita_projetada
            
            if novo_contrato != "Manter o mesmo":
                payload_sim["Contract"] = novo_contrato
                
            if payload_sim["InternetService"] != "No":
                if add_tech: payload_sim["TechSupport"] = "Yes"
                if add_sec: payload_sim["OnlineSecurity"] = "Yes"
                if add_prot: payload_sim["DeviceProtection"] = "Yes"
                if add_backup: payload_sim["OnlineBackup"] = "Yes"
                if add_stream_tv: payload_sim["StreamingTV"] = "Yes"
                if add_stream_mov: payload_sim["StreamingMovies"] = "Yes"
            
            try:
                with st.spinner("Calculando novo risco e viabilidade..."):
                    resposta_sim = requests.post(api_url, json=payload_sim, timeout=10)
                    prob_sim = resposta_sim.json()["probabilidade_churn"]
                    
                    st.divider()
                    st.subheader("2. Análise de Resultados (Antes vs. Depois)")
                    
                    col_graf1, col_graf2 = st.columns(2)
                    
                    with col_graf1:
                        fig1 = go.Figure(go.Indicator(
                            mode = "gauge+number", value = prob_atual, title = {'text': "Risco Original (%)"},
                            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "gray"}, 'steps': [
                                {'range': [0, 30], 'color': "#00cc96"}, {'range': [30, 70], 'color': "#FFA15A"}, {'range': [70, 100], 'color': "#EF553B"}
                            ]}
                        ))
                        st.plotly_chart(fig1, use_container_width=True)
                        
                    with col_graf2:
                        fig2 = go.Figure(go.Indicator(
                            mode = "gauge+number", value = prob_sim, title = {'text': "Risco Pós-Negociação (%)"},
                            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "black"}, 'steps': [
                                {'range': [0, 30], 'color': "#00cc96"}, {'range': [30, 70], 'color': "#FFA15A"}, {'range': [70, 100], 'color': "#EF553B"}
                            ]}
                        ))
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    st.subheader("3. Impacto Financeiro da Ação")
                    col_fin1, col_fin2, col_fin3 = st.columns(3)
                    
                    col_fin1.metric("Redução de Risco", f"{(prob_atual - prob_sim):.2f} p.p.")
                    col_fin2.metric("Custo da Retenção (Desconto)", f"R$ {valor_desconto_real:.2f}", delta="Investimento", delta_color="off")
                    
                    if prob_sim < 50:
                        col_fin3.metric("Receita Retida (Salva)", f"R$ {receita_projetada:.2f}", delta="Conta Salva!", delta_color="normal")
                    else:
                        col_fin3.metric("Receita Retida (Salva)", f"R$ 0.00", delta="Risco ainda alto", delta_color="inverse")
                        
            except:
                st.error("Erro de comunicação com a API.")

with tab4:
    st.title("Instruções")
    st.write(
        """Interface Streamlit para a API de previsão de Churn.

Pré-requisito: a API precisa estar rodando antes de usar esta tela:
    **uvicorn api:app --reload**

Para rodar esta interface:
    **streamlit run app.py**""")