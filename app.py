from dotenv import load_dotenv
import os
import streamlit as st
from database import init_db

load_dotenv()

GEMINI_KEY_ENV = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(
    page_title="Gabarito IA",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializa o banco na primeira execução
init_db()

# ── SESSION STATE ────────────────────────────────────────────────
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = GEMINI_KEY_ENV

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.title("📝 Gabarito IA")
    st.caption("Sistema de correção automática de provas")
    st.divider()

    st.subheader("Configuração da API")
    api_key = st.text_input(
        "Chave API Gemini",
        value=st.session_state.gemini_api_key,
        type="password",
        placeholder="AIza...",
        help="Obtenha sua chave gratuita em: aistudio.google.com",
    )

    if api_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key

    if st.session_state.gemini_api_key:
        st.success("API configurada")
    else:
        st.warning("Configure a chave API para usar a correção automática")

    st.divider()
    st.caption("Navegue pelas páginas no menu acima ↑")

# ── HOME ─────────────────────────────────────────────────────────
st.title("Sistema de Correção de Gabaritos com IA")
st.write("")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("**1. Cadastros**\n\nCadastre professores, turmas e alunos")

with col2:
    st.info("**2. Provas**\n\nCrie provas, defina questões, pesos e gabarito. Gere as folhas em PDF")

with col3:
    st.info("**3. Correção**\n\nFaça upload das fotos dos gabaritos. O sistema identifica o aluno pelo QR Code e corrige automaticamente")

with col4:
    st.info("**4. Relatório**\n\nVisualize as notas e exporte o Excel com matrícula e nota de cada aluno")

st.divider()
st.subheader("Como obter a chave API Gemini (gratuita)")
st.markdown("""
1. Acesse [aistudio.google.com](https://aistudio.google.com)
2. Faça login com sua conta Google
3. Clique em **Get API Key** -> **Create API key**
4. Copie a chave e cole no campo da sidebar
5. O plano gratuito permite **1.500 requisições por dia** (suficiente para o protótipo)
""")
