from PIL import Image
import streamlit as st
import google.generativeai as genai
from funcoes import *

# ---- ID da planilha ----
SHEET_ID = "1bgT0vsEx4dFGxtTQs7RU5jVvvtZsbHnjrpyPQ7tibn4"

st.set_page_config(page_title='AgroGuardian - Leitor de Imagens', page_icon=':robot:', layout='centered')
st.title('🌱AgroGuardian - Detecção de Pragas')
st.caption('Feito pelos alunos do 2°D Redes de Computadores')

# 🔑 Pega a chave direto dos segredos do Streamlit, ou usa valor local para desenvolvimento
if 'chave_api' not in st.session_state:
    try:
        chave_api = st.secrets["GEMINI_API_KEY"]
        if chave_api.startswith('AI'):
            st.session_state.chave_api = chave_api
            genai.configure(api_key=st.session_state.chave_api)
            st.sidebar.success('Chave API carregada com sucesso ✅')
        else:
            st.sidebar.error('Chave API inválida ❌')
    except Exception:
        # Para rodar local, coloque sua chave manualmente aqui:
        chave_api_local = "AIzaSyDvvCnRkPRKyeB8LRVmVHh11crJNlxxyT4"
        if chave_api_local.startswith('AI'):
            st.session_state.chave_api = chave_api_local
            genai.configure(api_key=st.session_state.chave_api)
            st.sidebar.info('Chave API carregada localmente para desenvolvimento ⚠️')
        else:
            st.sidebar.error('Chave API local inválida ❌')

modelo = genai.GenerativeModel('gemini-2.0-flash')
culturas = carregar_culturas()

with st.form(key='formulario_analise'):
    prompt = st.text_input(label='Digite sua dúvida agrícola', placeholder='Ex: Qual é essa praga e como combater?')
    imagem_envio = st.file_uploader(label='Envie uma imagem da planta afetada', type=['jpg', 'jpeg', 'png'])
    enviar = st.form_submit_button('Analisar imagem')

if enviar:
    if prompt == '':
        st.error('Por favor, anexe uma imagem antes de prosseguir.')
    elif imagem_envio is None:
        st.error('Por favor, envie uma imagem antes de enviar.')
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

            # Salvar no Google Sheets
            salvar_historico_online(prompt, resposta, imagem_envio.name, SHEET_ID)

        except Exception as e:
            st.error(f"Erro: {str(e)}")

# ---- Mostrar histórico online ----
st.sidebar.subheader("📜 Histórico de Consultas")
historico = carregar_historico_online(SHEET_ID)
if historico:
    for linha in historico[1:]:
        st.sidebar.write(f"**{linha[0]}** - {linha[1]}")
else:
    st.sidebar.write("Nenhuma consulta registrada ainda.")
