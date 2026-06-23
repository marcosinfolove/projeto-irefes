import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard IREFES - Rugby CR", layout="wide")

# Estilo personalizado (Alto Contraste)
st.markdown("""
    <style>
    .main { font-size: 1.15rem; }
    .stMetric { background-color: #0e1117; padding: 18px; border-radius: 12px; border: 1px solid #1e293b; }
    .info-box { background-color: #0f172a; border: 1px solid #334155; padding: 20px; border-radius: 12px; margin-top: 15px; color: #94a3b8; }
    /* Estilo para o link da planilha parecer um botão na barra lateral */
    .link-button {
        display: inline-block;
        padding: 10px 20px;
        background-color: #22c55e;
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏉 Sistema de BI com Acessibilidade - IREFES")
st.markdown("Painel de Performance e Acompanhamento Físico para Rugby em Cadeira de Rodas.")

# LINKS DAS FONTES DE DADOS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS_4awyPRfqe_rWxYZibAEo91cOFaiUPRKigBAanzMZUzdoM4kNAFfDQ0xprCnfCknO1gsD8Cx_onHO/pub?gid=0&single=true&output=csv"
URL_PLANILHA_EDITAVEL = "https://docs.google.com/spreadsheets/d/1j_AdsLaoLv3lmcstT9Oe5FonzViKvZYelVx9cNCdWogs/edit?usp=sharing"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        df = pd.read_csv(url)
        df['Sprint 20m'] = pd.to_numeric(df['Sprint 20m'], errors='coerce')
        df['Arremesso'] = pd.to_numeric(df['Arremesso'], errors='coerce')
        df['Classe Funcional'] = df['Classe Funcional'].astype(str)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados. Detalhe: {e}")
        return pd.DataFrame()

df = carregar_dados(URL_CSV)

if not df.empty:
    # --- BARRA LATERAL (ACESSIBILIDADE & DIRECIONAMENTO) ---
    st.sidebar.header("🔍 Painel de Seleção")
    lista_atletas = ["Todos"] + list(df['Atleta'].dropna().unique())
    atleta_selecionado = st.sidebar.selectbox("Selecione o Atleta:", lista_atletas)
    
    st.sidebar.divider()
    
    # SEÇÃO DE EXPLICAÇÃO QUE VOCÊ PEDIU
    st.sidebar.markdown("### ♿ Coleta Assistida (I.A. Workspace)")
    
    # Botão de direcionamento direto para a planilha
    st.sidebar.markdown(f'<a href="{URL_PLANILHA_EDITAVEL}" target="_blank" class="link-button">📂 Abrir Planilha de Coleta</a>', unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    **Instruções para Atletas PcD:**
    
    1. Clique no botão acima para abrir a base de dados.
    2. No Google Sheets, abra o painel do **Gemini/Assistente** à direita.
    3. Clique no campo de chat e use **Windows + H** para ditar comandos.
    4. **Exemplo:** *"Adicione uma linha para o Marcos com Sprint 8.5"*.
    5. O sistema processa sua voz e insere os dados sem você precisar clicar em células pequenas.
    """)

    # --- RESTANTE DO DASHBOARD (Gráficos e Filtros) ---
    if atleta_selecionado == "Todos":
        st.subheader("📋 Tabela Geral de Resultados")
        st.dataframe(df, use_container_width=True)
        st.divider()
        
        st.subheader("📊 Análise Visual de Desempenho")
        col1, col2 = st.columns(2)
        with col1:
            fig_sprint = px.bar(df, x='Atleta', y='Sprint 20m', title='Velocidade (Menor = Melhor)', color='Classe Funcional', text_auto=True)
            st.plotly_chart(fig_sprint, use_container_width=True)
        with col2:
            fig_forca = px.bar(df, x='Atleta', y='Arremesso', title='Força (Maior = Melhor)', color='Classe Funcional', text_auto=True)
            st.plotly_chart(fig_forca, use_container_width=True)
    else:
        st.subheader(f"📊 Evolução Individual: {atleta_selecionado}")
        dados_atleta = df[df['Atleta'] == atleta_selecionado].iloc[0]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Classe Funcional", dados_atleta['Classe Funcional'])
        c2.metric("Sprint 20m", f"{dados_atleta['Sprint 20m']} s")
        c3.metric("Arremesso", f"{dados_atleta['Arremesso']} m")
        c4.metric("PSE (Esforço)", dados_atleta['PSE'] if 'PSE' in df.columns else "N/A")
        
        st.divider()
        st.markdown("### Comparativo Individual vs Média da Equipe")
        
        media_sprint = df['Sprint 20m'].mean()
        media_arremesso = df['Arremesso'].mean()
        comp_df = pd.DataFrame({
            "Métrica": ["Sprint 20m", "Sprint 20m", "Arremesso", "Arremesso"],
            "Referência": [dados_atleta['Atleta'], "Média Equipe", dados_atleta['Atleta'], "Média Equipe"],
            "Valor": [dados_atleta['Sprint 20m'], media_sprint, dados_atleta['Arremesso'], media_arremesso]
        })
        
        fig_comp = px.bar(comp_df, x="Métrica", y="Valor", color="Referência", barmode="group",
                         labels={"Valor": "Pontuação", "Referência": "Tipo de Medição"},
                         color_discrete_map={dados_atleta['Atleta']: '#00CC96', 'Média Equipe': '#AB63FA'})
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.warning("Nenhum dado encontrado. Conecte sua base de dados do Google Drive.")
