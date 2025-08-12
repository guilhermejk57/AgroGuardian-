from PIL import Image
import streamlit as st
import google.generativeai as genai
from funcoes import *

st.set_page_config(page_title='AgroGuardian - Leitor de Imagens', page_icon=':robot:', layout='centered')
st.title('🌱AgroGuardian - Detecção de Pragas')
st.caption('Feito pelos alunos do 2°D Redes de Computadores')

# 🔑 Pega a chave direto dos segredos do Streamlit
if 'chave_api' not in st.session_state:
    try:
        chave_api = st.secrets["GEMINI_API_KEY"]
        if chave_api.startswith('AI'):
            st.session_state.chave_api = chave_api
            genai.configure(api_key=st.session_state.chave_api)
            st.sidebar.success('Chave API carregada com sucesso ✅')
        else:
            st.sidebar.error('Chave API inválida ❌')
    except KeyError:
        st.sidebar.error('A chave GEMINI_API_KEY não foi configurada nos Secrets')

modelo = genai.GenerativeModel('gemini-2.0-flash')

culturas = carregar_culturas()

# Usar formulário para permitir enviar com Enter
with st.form(key='formulario_analise'):
    prompt = st.text_input(label='Digite sua dúvida agrícola', placeholder='Ex: Qual é essa praga e como combater?')
    imagem_envio = st.file_uploader(label='Envie uma imagem da planta afetada', type=['jpg', 'jpeg', 'png'])
    enviar = st.form_submit_button('Analisar imagem')

if enviar:
    if prompt == '':
        st.error('Por favor, digite sua dúvida agrícola antes de enviar.')
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

            salvar_historico(prompt, resposta, imagem_envio.name)

        except Exception as e:
            st.error(f"Erro: {str(e)}")


# api: AIzaSyDvvCnRkPRKyeB8LRVmVHh11crJNlxxyT4


