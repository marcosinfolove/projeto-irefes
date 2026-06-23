import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard IREFES - Rugby CR", layout="wide")

# Estilo personalizado de alto contraste para melhorar usabilidade e acessibilidade
st.markdown("""
    <style>
    .main { font-size: 1.15rem; }
    .stMetric { background-color: #0e1117; padding: 18px; border-radius: 12px; border: 1px solid #1e293b; }
    .ai-box { background-color: #1e1b4b; border: 1px solid #4338ca; padding: 20px; border-radius: 12px; margin-top: 15px; color: #e0e7ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏉 Sistema de BI com Acessibilidade e I.A. - IREFES")
st.markdown("Painel de Performance para Rugby em Cadeira de Rodas integrado com Inteligência Artificial.")

# LINK PERFEITO DA SUA PLANILHA DO GOOGLE DRIVE
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

def analisar_com_gemini(prompt, system_prompt, api_key):
    """
    Realiza uma chamada direta de REST API para o modelo Gemini 3-flash-preview.
    Mantém o código leve, estável e livre de dependências pesadas do SDK.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na API do Gemini (Código {response.status_code}): {response.text}"
    except Exception as e:
        return f"Não foi possível conectar ao servidor da Gemini. Detalhe: {e}"

if not df.empty:
    # --- BARRA LATERAL (ACESSIBILIDADE, FILTRO E I.A.) ---
    st.sidebar.header("🔍 Painel de Seleção")
    
    lista_atletas = ["Todos"] + list(df['Atleta'].dropna().unique())
    atleta_selecionado = st.sidebar.selectbox("Selecione o Atleta:", lista_atletas)
    
    st.sidebar.divider()
    st.sidebar.header("🤖 Configurações de I.A.")
    st.sidebar.markdown("[Como obter uma chave Gemini API gratuita?](https://aistudio.google.com/)", unsafe_allow_html=True)
    gemini_key = st.sidebar.text_input("Chave API do Gemini:", type="password", placeholder="Cole sua chave AI Studio aqui...")

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
            
        st.subheader("🤖 Assistente de Análise Coletiva IREFES")
        if gemini_key:
            if st.button("Gerar Diagnóstico de Desempenho do Elenco via I.A."):
                with st.spinner("Analisando dados com o Gemini..."):
                    system_prompt = (
                        "Você é um renomado fisiologista esportivo e consultor de alta performance "
                        "especialista em Rugby em Cadeira de Rodas (Quad Rugby). Suas análises devem ser "
                        "altamente profissionais, encorajadoras, focadas em usabilidade e nas necessidades "
                        "de otimização física dos atletas."
                    )
                    
                    # Prepara os dados para mandar pro modelo de forma compacta
                    tabela_texto = df[['Atleta', 'Classe Funcional', 'Sprint 20m', 'Arremesso', 'PSE']].to_string()
                    prompt = (
                        f"Abaixo está a planilha de performance física da equipe IREFES:\n\n{tabela_texto}\n\n"
                        "Gere um diagnóstico de desempenho do elenco estruturado contendo:\n"
                        "1. Análise geral das médias do time em Sprint (velocidade) e Arremesso (força).\n"
                        "2. Destaques de atletas que possuem excelente desempenho considerando suas limitações de classe funcional.\n"
                        "3. Recomendações coletivas de treino preventivo e controle de esforço (PSE) baseado nos dados apresentados."
                    )
                    
                    analise_ia = analisar_com_gemini(prompt, system_prompt, gemini_key)
                    st.markdown(f"<div class='ai-box'><h3>✨ Relatório Estratégico do Elenco:</h3><br>{analise_ia}</div>", unsafe_allow_html=True)
        else:
            st.info("Insira sua Chave API do Gemini na barra lateral para habilitar o Diagnóstico Coletivo por I.A.!")

    else:
        # --- VISÃO FILTRADA DE APENAS UM ATLETA ---
        st.subheader(f"📊 Relatório Individual de Desempenho: {atleta_selecionado}")
        dados_atleta = df[df['Atleta'] == atleta_selecionado].iloc[0]
        
        # Cards de Destaque Métrico
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
        
        # DataFrame reestruturado corretamente para evitar o bug de legendas em inglês
        comp_data = {
            "Métrica": ["Sprint 20m", "Sprint 20m", "Arremesso", "Arremesso"],
            "Referência": [dados_atleta['Atleta'], "Média da Equipe", dados_atleta['Atleta'], "Média da Equipe"],
            "Valor": [dados_atleta['Sprint 20m'], media_sprint, dados_atleta['Arremesso'], media_arremesso]
        }
        comp_df = pd.DataFrame(comp_data)
        
        # Gráficos com legendas 100% em português nativo
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
        
        st.subheader(f"🤖 Assistente de Treinamento Inteligente (Gemini) para {atleta_selecionado}")
        if gemini_key:
            if st.button(f"Gerar Plano de Evolução Física Individual"):
                with st.spinner("Analisando o perfil do atleta com a I.A..."):
                    system_prompt = (
                        "Você é um preparador físico de Quad Rugby especializado em esportes adaptados e "
                        "tecnologias assistivas. Você deve gerar orientações altamente acessíveis e focadas "
                        "na classificação funcional do atleta em questão."
                    )
                    
                    prompt = (
                        f"Atleta analisado: {dados_atleta['Atleta']}\n"
                        f"Classe Funcional de Rugby: {dados_atleta['Classe Funcional']}\n"
                        f"Tempo no Sprint 20m: {dados_atleta['Sprint 20m']} segundos (Média geral do time: {media_sprint:.2f} s)\n"
                        f"Distância no Arremesso de Med Ball: {dados_atleta['Arremesso']} metros (Média geral do time: {media_arremesso:.2f} m)\n"
                        f"Percepção Subjetiva de Esforço (PSE): {dados_atleta['PSE']}\n\n"
                        "Escreva um Parecer de Evolução Física Individual contendo:\n"
                        "1. Uma avaliação objetiva se o atleta está acima ou abaixo das médias da equipe na sua categoria motora.\n"
                        "2. Um mini plano de treino (exemplo: exercícios específicos de força de core ou aceleração) seguro para sua classe funcional.\n"
                        "3. Recomendações para que o atleta possa interagir autonomamente com seu processo esportivo usando tecnologias assistivas."
                    )
                    
                    analise_ia = analisar_com_gemini(prompt, system_prompt, gemini_key)
                    st.markdown(f"<div class='ai-box'><h3>✨ Parecer e Planejamento Individual:</h3><br>{analise_ia}</div>", unsafe_allow_html=True)
        else:
            st.info("Insira sua Chave API do Gemini na barra lateral para habilitar a geração de Planos Individuais!")

else:
    st.warning("Nenhum dado encontrado. Conecte sua base de dados do Google Drive.")
