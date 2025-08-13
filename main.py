from PIL import Image
import streamlit as st
import google.generativeai as genai
import json
from funcoes import *

# Configurações básicas
st.set_page_config(page_title='AgroGuardian - Leitor de Imagens', page_icon=':robot:', layout='centered')
st.title('🌱 AgroGuardian - Detecção de Pragas')
st.caption('Feito pelos alunos do 2°D Redes de Computadores')

# Tente pegar as credenciais do Streamlit Secrets
try:
    chave_api = st.secrets["GEMINI_API_KEY"]
except Exception:
    chave_api = "SUA_CHAVE_GEMINI_AQUI"  # coloque sua chave local para testes

try:
    google_creds_json = st.secrets["GOOGLE_CREDENTIALS_JSON"]
    google_creds_dict = json.loads(google_creds_json)
except Exception:
    st.error("Erro ao carregar credenciais do Google do secrets.toml")
    google_creds_dict = None

try:
    SHEET_ID = st.secrets["SHEET_ID"]
except Exception:
    SHEET_ID = "SEU_ID_DA_PLANILHA"

# Configurar API Gemini
if chave_api.startswith('AI'):
    genai.configure(api_key=chave_api)
    modelo = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("Chave Gemini API inválida!")

culturas = carregar_culturas()

with st.form(key='formulario_analise'):
    prompt = st.text_input('Digite sua dúvida agrícola', placeholder='Ex: Qual é essa praga e como combater?')
    imagem_envio = st.file_uploader('Envie uma imagem da planta afetada', type=['jpg', 'jpeg', 'png'])
    enviar = st.form_submit_button('Analisar imagem')

if enviar:
    if prompt == '':
        st.error('Por favor, digite sua dúvida.')
    elif imagem_envio is None:
        st.error('Por favor, envie uma imagem.')
    else:
        try:
            dados_imagem = imagem2bytes(imagem_envio)
            resposta = resposta_gemini(modelo, dados_imagem, prompt)

            col1, col2 = st.columns(2)
            with col1:
                imagem = Image.open(imagem_envio)
                st.image(imagem, use_container_width=True)

            with col2:
                st.subheader('Diagnóstico:')
                st.write(resposta)

            if google_creds_dict:
                salvar_historico_online(prompt, resposta, imagem_envio.name, SHEET_ID, google_creds_dict)
            else:
                st.warning("Histórico não salvo: credenciais do Google não configuradas.")

        except Exception as e:
            st.error(f"Erro: {e}")

# Mostrar histórico online no sidebar
if google_creds_dict:
    try:
        historico = carregar_historico_online(SHEET_ID, google_creds_dict)
        st.sidebar.subheader("📜 Histórico de Consultas")
        if historico:
            for linha in historico[1:]:
                st.sidebar.write(f"**{linha[0]}** - {linha[1]}")
        else:
            st.sidebar.write("Nenhuma consulta registrada ainda.")
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar histórico: {e}")
else:
    st.sidebar.info("Configure as credenciais do Google para ver o histórico.")
