from PIL import Image
import streamlit as st
import google.generativeai as genai
import json
from funcoes import *

# Configurações da página
st.set_page_config(page_title='AgroGuardian - Leitor de Imagens', page_icon=':robot:', layout='centered')
st.title('🌱 AgroGuardian - Detecção de Pragas')
st.caption('Feito pelos alunos do 2°D Redes de Computadores')

# Carregar credenciais do Streamlit secrets
try:
    chave_api = st.secrets["GEMINI_API_KEY"]
except Exception:
    chave_api = "SUA_CHAVE_GEMINI_AQUI"

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

# Formulário principal
with st.form(key='formulario_analise'):
    usuario = st.text_input("Digite seu nome ou email")  # identificação do usuário
    prompt = st.text_input('Digite sua dúvida agrícola', placeholder='Ex: Qual é essa praga e como combater?')
    imagem_envio = st.file_uploader('Envie uma imagem da planta afetada', type=['jpg', 'jpeg', 'png'])
    enviar = st.form_submit_button('Analisar imagem')

if enviar:
    if usuario.strip() == "":
        st.error("Por favor, digite seu nome ou email.")
    elif prompt == '':
        st.error('Por favor, digite sua dúvida.')
    elif imagem_envio is None:
        st.error('Por favor, envie uma imagem.')
    else:
        try:
            # Processar a imagem e obter resposta do Gemini
            dados_imagem = imagem2bytes(imagem_envio)
            resposta = resposta_gemini(modelo, dados_imagem, prompt)

            # Exibir imagem + diagnóstico lado a lado
            col1, col2 = st.columns(2)
            with col1:
                imagem = Image.open(imagem_envio)
                st.image(imagem, use_container_width=True)

            with col2:
                st.subheader('Diagnóstico:')
                st.write(resposta)

            # Salvar histórico na planilha
            if google_creds_dict:
                salvar_historico_online(usuario, prompt, resposta, imagem_envio.name, SHEET_ID, google_creds_dict)
            else:
                st.warning("Histórico não salvo: credenciais do Google não configuradas.")

        except Exception as e:
            st.error(f"Erro: {e}")

# Mostrar histórico no sidebar
if google_creds_dict:
    try:
        historico = carregar_historico_online(SHEET_ID, google_creds_dict)
        st.sidebar.subheader("📜 Histórico de Consultas")

        senha_admin = st.sidebar.text_input("Senha de administrador", type="password")

        if senha_admin == st.secrets.get("ADMIN_PASS", "admin123"):
            # Admin vê tudo
            for linha in historico[1:]:
                st.sidebar.write(f"**{linha[0]} - {linha[1]}** → {linha[2]}")
        else:
            # Usuário só vê o dele
            if "usuario" in locals() and usuario.strip():
                historico_usuario = [linha for linha in historico[1:] if linha[1] == usuario]
                if historico_usuario:
                    for linha in historico_usuario:
                        st.sidebar.write(f"**{linha[0]}** → {linha[2]}")
                else:
                    st.sidebar.write("Nenhuma consulta registrada ainda.")
            else:
                st.sidebar.info("Digite seu nome no formulário para ver seu histórico.")

    except Exception as e:
        st.sidebar.error(f"Erro ao carregar histórico: {e}")
else:
    st.sidebar.info("Configure as credenciais do Google para ver o histórico.")
