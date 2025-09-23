import streamlit as st
from funcoes import carregar_culturas, resposta_gemini, imagem2bytes, conectar_google_sheets, salvar_historico_online, carregar_historico_online
import json
import google.generativeai as genai

# --- Configuração da página ---
st.set_page_config(
    page_title="AgroGuardian",
    page_icon="images/icone.jpg",  # caminho do seu ícone
    layout="wide"
)

# --- CSS personalizado ---
st.markdown("""
    <style>
        /* Fundo geral */
        .stApp {
            background-color: #f8f9fa;
        }

        /* Título estilizado */
        .custom-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            color: #2d6a4f;
            margin-bottom: 10px;
        }

        /* Subtítulo */
        .custom-subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #40916c;
            margin-bottom: 25px;
        }

        /* Botões */
        .stButton>button {
            background-color: #52b788;
            color: white;
            border-radius: 12px;
            border: none;
            padding: 10px 20px;
            font-size: 1rem;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #40916c;
            transform: scale(1.05);
        }

        /* Caixas de texto */
        textarea, input {
            border-radius: 10px !important;
            border: 1px solid #52b788 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- HTML para título e subtítulo ---
st.markdown("<div class='custom-title'>🌱 AgroGuardian</div>", unsafe_allow_html=True)
st.markdown("<div class='custom-subtitle'>Seu assistente para agricultura inteligente</div>", unsafe_allow_html=True)

# --- Carregar culturas ---
culturas = carregar_culturas()

# --- Carregar chaves do Streamlit Secrets ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SHEET_ID = st.secrets["SHEET_ID"]
GOOGLE_CREDENTIALS_JSON = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])

# --- Configurar modelo Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel("gemini-1.5-flash")

# --- Conectar ao Google Sheets ---
cliente = conectar_google_sheets(GOOGLE_CREDENTIALS_JSON)

# --- Interface principal ---
st.header("📸 Análise de Imagens de Plantas")

imagem_upload = st.file_uploader("Envie uma imagem da planta", type=["jpg", "jpeg", "png"])
prompt = st.text_area("Descreva o problema ou dúvida (opcional):")

if st.button("🔍 Analisar"):
    try:
        if imagem_upload:
            img_bytes = imagem2bytes(imagem_upload)
            resposta = resposta_gemini(modelo, img_bytes, prompt)
            st.success("✅ Resultado da análise:")
            st.write(resposta)

            salvar_historico_online(cliente, SHEET_ID, "Usuário", prompt, resposta, imagem_upload.name)

        else:
            st.warning("⚠️ Por favor, envie uma imagem para análise.")

    except Exception as e:
        st.error(f"Erro: {e}")

# --- Histórico ---
if st.checkbox("📜 Mostrar histórico"):
    historico = carregar_historico_online(cliente, SHEET_ID)
    st.dataframe(historico)
