import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard IREFES - Rugby CR", layout="wide")

# Estilo para melhorar a visualização (Acessibilidade)
st.markdown("""
    <style>
    .main { font-size: 1.2rem; }
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏉 Sistema de BI com Acessibilidade - IREFES")
st.markdown("Monitoramento de Performance para Rugby em Cadeira de Rodas")

# LINK DA SUA PLANILHA (O mesmo que já funciona)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS_4awyPRfqe_rWxYZibAEo91cOFaiUPRKigBAanzMZUzdoM4kNAFfDQ0xprCnfCknO1gsD8Cx_onHO/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        df = pd.read_csv(url)
        # Limpeza básica de dados
        df['Sprint 20m'] = pd.to_numeric(df['Sprint 20m'], errors='coerce')
        df['Arremesso'] = pd.to_numeric(df['Arremesso'], errors='coerce')
        df['Classe Funcional'] = df['Classe Funcional'].astype(str)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = carregar_dados(URL_PLANILHA)

if not df.empty:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("🔍 Filtros de Acessibilidade")
    
    # Opção para ver todos ou um específico
    lista_atletas = ["Todos"] + list(df['Atleta'].unique())
    atleta_selecionado = st.sidebar.selectbox("Selecione um Atleta para análise individual:", lista_atletas)

    if atleta_selecionado == "Todos":
        st.subheader("📋 Visão Geral da Equipe")
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(df, x='Atleta', y='Sprint 20m', title='Velocidade (s) - Menor é Melhor', color='Classe Funcional', text_auto=True)
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.bar(df, x='Atleta', y='Arremesso', title='Força (m) - Maior é Melhor', color='Classe Funcional', text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)
    
    else:
        # --- VISÃO INDIVIDUAL DO ATLETA ---
        st.subheader(f"📊 Relatório Individual: {atleta_selecionado}")
        dados_atleta = df[df['Atleta'] == atleta_selecionado].iloc[0]
        
        # Métricas em destaque (Cards)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Classe Funcional", dados_atleta['Classe Funcional'])
        c2.metric("Sprint 20m", f"{dados_atleta['Sprint 20m']}s")
        c3.metric("Arremesso", f"{dados_atleta['Arremesso']}m")
        c4.metric("PSE (Esforço)", dados_atleta['PSE'])

        # Comparação rápida com a média da equipe
        st.divider()
        st.markdown("### Comparativo com a Média da Equipe")
        
        media_sprint = df['Sprint 20m'].mean()
        media_arremesso = df['Arremesso'].mean()
        
        comp_df = pd.DataFrame({
            "Métrica": ["Sprint (s)", "Arremesso (m)"],
            "Atleta": [dados_atleta['Sprint 20m'], dados_atleta['Arremesso']],
            "Média Equipe": [media_sprint, media_arremesso]
        })
        
        fig_comp = px.bar(comp_df, x="Métrica", y=["Atleta", "Média Equipe"], barmode="group", title="Performance Individual vs Média")
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.warning("Aguardando conexão com a base de dados...")
