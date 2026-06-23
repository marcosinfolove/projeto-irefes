import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard IREFES - Rugby CR", layout="wide")

# Estilo personalizado de alto contraste para usabilidade e acessibilidade
st.markdown("""
    <style>
    .main { font-size: 1.15rem; }
    .stMetric { background-color: #0e1117; padding: 18px; border-radius: 12px; border: 1px solid #1e293b; }
    .info-box { background-color: #0f172a; border: 1px solid #334155; padding: 20px; border-radius: 12px; margin-top: 15px; color: #94a3b8; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏉 Sistema de BI com Acessibilidade - IREFES")
st.markdown("Painel de Performance e Acompanhamento Físico para Rugby em Cadeira de Rodas.")

# LINK DA PLANILHA DO GOOGLE DRIVE
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS_4awyPRfqe_rWxYZibAEo91cOFaiUPRKigBAanzMZUzdoM4kNAFfDQ0xprCnfCknO1gsD8Cx_onHO/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60) # Atualiza automaticamente a cada 60 segundos
def carregar_dados(url):
    try:
        df = pd.read_csv(url)
        # Força conversões corretas de tipo de dado
        df['Sprint 20m'] = pd.to_numeric(df['Sprint 20m'], errors='coerce')
        df['Arremesso'] = pd.to_numeric(df['Arremesso'], errors='coerce')
        df['Classe Funcional'] = df['Classe Funcional'].astype(str)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Google Sheets. Detalhe: {e}")
        return pd.DataFrame()

df = carregar_dados(URL_PLANILHA)

if not df.empty:
    # --- BARRA LATERAL (FILTRAGEM E ACESSIBILIDADE) ---
    st.sidebar.header("🔍 Painel de Seleção")
    
    lista_atletas = ["Todos"] + list(df['Atleta'].dropna().unique())
    atleta_selecionado = st.sidebar.selectbox("Selecione o Atleta:", lista_atletas)
    
    st.sidebar.divider()
    st.sidebar.markdown("""
    ### ♿ Coleta Acessível por Voz
    Para atletas com limitação motora severa:
    
    **Opção 1: Digitação Direta no Campo de Texto**
    1. Abra a planilha do Google Drive.
    2. Dê um **duplo clique** na célula ou clique na **barra de fórmulas (campo de texto)** no topo para que o cursor fique ativo.
    3. Pressione **Windows + H** para abrir o microfone nativo e ditar o valor.
    
    **Opção 2: Chat Assistido (Inteligente)**
    - Clique na barra de entrada de texto do painel assistente do Workspace à direita, digite ou dite o comando de inserção de dados e ele aplicará o valor diretamente na célula desejada!
    """)

    if atleta_selecionado == "Todos":
        st.subheader("📋 Tabela Geral de Resultados")
        st.dataframe(df, use_container_width=True)
        st.divider()
        
        st.subheader("📊 Análise Visual de Desempenho")
        col1, col2 = st.columns(2)
        with col1:
            fig_sprint = px.bar(df, x='Atleta', y='Sprint 20m', 
                                title='Velocidade: Sprint 20m (Menor = Melhor)', 
                                color='Classe Funcional', text_auto=True)
            fig_sprint.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_sprint, use_container_width=True)
        with col2:
            fig_forca = px.bar(df, x='Atleta', y='Arremesso', 
                               title='Força: Arremesso Med. Ball (Maior = Melhor)', 
                               color='Classe Funcional', text_auto=True)
            fig_forca.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_forca, use_container_width=True)
            
        st.markdown("""
        <div class='info-box'>
        <h3>💡 Instruções de Uso para a Comissão Técnica:</h3>
        <p>Este painel consolida os dados de performance esportiva coletados durante os testes. 
        Utilize os filtros no menu lateral para focar na evolução de um atleta específico ou comparar resultados individuais contra as médias do elenco.</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        # --- VISÃO FILTRADA DE APENAS UM ATLETA ---
        st.subheader(f"📊 Relatório Individual de Desempenho: {atleta_selecionado}")
        dados_atleta = df[df['Atleta'] == atleta_selecionado].iloc[0]
        
        # Cards de Destaque Métrico de alto contraste
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Classe Funcional", dados_atleta['Classe Funcional'])
        c2.metric("Sprint 20m", f"{dados_atleta['Sprint 20m']} s")
        c3.metric("Arremesso", f"{dados_atleta['Arremesso']} m")
        c4.metric("Nível de Cansaço (PSE)", dados_atleta['PSE'] if 'PSE' in df.columns else "N/A")
        
        st.divider()
        st.markdown("### Comparativo de Performance com a Média")
        
        # Cálculo das médias de comparação
        media_sprint = df['Sprint 20m'].mean()
        media_arremesso = df['Arremesso'].mean()
        
        # DataFrame estruturado para manter as legendas em português
        comp_data = {
            "Métrica": ["Sprint 20m", "Sprint 20m", "Arremesso", "Arremesso"],
            "Referência": [dados_atleta['Atleta'], "Média da Equipe", dados_atleta['Atleta'], "Média da Equipe"],
            "Valor": [dados_atleta['Sprint 20m'], media_sprint, dados_atleta['Arremesso'], media_arremesso]
        }
        comp_df = pd.DataFrame(comp_data)
        
        fig_comp = px.bar(
            comp_df,
            x="Métrica",
            y="Valor",
            color="Referência",
            barmode="group",
            title="Comparação Direta do Atleta contra Média do Grupo",
            labels={"Valor": "Pontuação", "Referência": "Tipo de Medição"},
            color_discrete_map={dados_atleta['Atleta']: '#00CC96', 'Média da Equipe': '#AB63FA'}
        )
        
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.warning("Nenhum dado encontrado. Conecte sua base de dados do Google Drive.")
