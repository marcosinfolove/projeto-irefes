import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard IREFES", layout="wide")

st.title("🏉 Dashboard de Desempenho Físico - IREFES")
st.markdown("Painel integrado automaticamente com o Google Sheets.")

# --- CONEXÃO COM O GOOGLE SHEETS ---
# SUBSTITUA O TEXTO ABAIXO PELO LINK DE COMPARTILHAMENTO DA SUA PLANILHA
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS_4awyPRfqe_rWxYZibAEo91cOFaiUPRKigBAanzMZUzdoM4kNAFfDQ0xprCnfCknO1gsD8Cx_onHO/pub?output=csv"

@st.cache_data(ttl=60) # Atualiza os dados a cada 60 segundos
def carregar_dados(url):
    try:
        # Transforma o link de visualização em um link de exportação de dados
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a planilha. Verifique se o link está como 'Qualquer pessoa com o link'. Detalhe: {e}")
        return pd.DataFrame()

df = carregar_dados(URL_PLANILHA)

# --- CRIAÇÃO DO DASHBOARD ---
if not df.empty:
    st.subheader("📋 Tabela Geral de Resultados")
    st.dataframe(df, use_container_width=True)
    st.divider()

    st.subheader("📊 Análise Visual de Desempenho")
    col1, col2 = st.columns(2)

    with col1:
        fig_sprint = px.bar(df, x='Atleta', y='Sprint 20m', 
                            title='Velocidade: Sprint 20m (Menor = Melhor)',
                            color='Classe Funcional', text_auto=True)
        # Código que resolve o problema dos nomes sobrepostos (inclina em 45 graus)
        fig_sprint.update_xaxes(tickangle=-45) 
        st.plotly_chart(fig_sprint, use_container_width=True)

    with col2:
        fig_forca = px.bar(df, x='Atleta', y='Arremesso', 
                           title='Força: Arremesso Med. Ball (Maior = Melhor)',
                           color='Classe Funcional', text_auto=True)
        # Código que resolve o problema dos nomes sobrepostos
        fig_forca.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_forca, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado ou erro na conexão com a planilha.")
