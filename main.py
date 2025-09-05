from PIL import Image
import streamlit as st
import google.generativeai as genai
import json
from funcoes import (
    carregar_culturas,
    resposta_gemini,
    imagem2bytes,
    conectar_google_sheets,
    salvar_historico_online,
    carregar_historico_online,
)

# Configuração da página
st.set_page_config(page_title="AgroGuardian", layout="wide")
st.title("🌱 AgroGuardian")
st.caption("Diagnóstico de pragas em culturas agrícolas usando Gemini")

# Segredos (API e credenciais)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "SUA_CHAVE_GEMINI_AQUI")
GOOGLE_CREDENTIALS_JSON = st.secrets.get("GOOGLE_CREDENTIALS_JSON", None)
SHEET_ID = st.secrets.get("SHEET_ID", "SEU_ID_DA_PLANILHA")

if GOOGLE_CREDENTIALS_JSON:
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
else:
    creds_dict = None
    st.warning("⚠️ Credenciais do Google não configuradas. Histórico não será salvo.")

# Configuração do Gemini
if GEMINI_API_KEY.startswith("AI"):
    genai.configure(api_key=GEMINI_API_KEY)
    modelo = genai.GenerativeModel("gemini-2.0-flash")
else:
    st.error("Chave Gemini API inválida. Configure em st.secrets.")
    modelo = None

# Carregar culturas
culturas = carregar_culturas()

# Sidebar
menu = st.sidebar.radio("Menu", ["Nova consulta", "Histórico"])

# --- Nova consulta ---
if menu == "Nova consulta":
    with st.form("consulta_form"):
        usuario = st.text_input(
            "Seu nome ou e-mail",
            placeholder="Ex: João Silva ou joao@email.com"
        )

        # selectbox com culturas
        cultura_selecionada = st.selectbox(
            "Selecione a cultura",
            ["(não especificar)"] + list(culturas.keys())
        )

        prompt = st.text_area(
            "Descreva sua dúvida sobre a praga",
            placeholder="Ex: As folhas da soja estão amareladas com manchas escuras..."
        )

        imagem_envio = st.file_uploader(
            "Envie uma imagem da planta",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=False
        )

        submit = st.form_submit_button("Analisar imagem")

    if submit:
        if not usuario.strip():
            st.error("Informe seu nome ou e-mail!")
        elif not prompt.strip():
            st.error("Digite uma descrição da sua dúvida!")
        elif not imagem_envio:
            st.error("Envie uma imagem da planta!")
        else:
            try:
                dados_imagem = imagem2bytes(imagem_envio)

                # prompt reforçado com cultura (se selecionada)
                if cultura_selecionada != "(não especificar)":
                    prompt_completo = (
                        f"O usuário selecionou a cultura **{cultura_selecionada}**. "
                        f"As pragas mais comuns para essa cultura são: {', '.join(culturas[cultura_selecionada])}. "
                        f"Agora responda considerando a imagem e essa informação: {prompt}"
                    )
                else:
                    prompt_completo = prompt

                resposta = resposta_gemini(modelo, dados_imagem, prompt_completo)

                col1, col2 = st.columns(2)
                with col1:
                    imagem = Image.open(imagem_envio)
                    st.image(imagem, caption="Imagem enviada", use_container_width=True)
                with col2:
                    st.subheader("Diagnóstico")
                    st.write(resposta)

                    # mostra pragas comuns apenas se cultura aparecer na resposta do Gemini
                    if cultura_selecionada != "(não especificar)" and cultura_selecionada.lower() in resposta.lower():
                        pragas_comuns = culturas[cultura_selecionada]
                        st.info(
                            f"🔎 Para a cultura **{cultura_selecionada}**, "
                            f"as pragas mais comuns são: {', '.join(pragas_comuns)}."
                        )

                # salvar histórico online (se credenciais existirem)
                if creds_dict:
                    cliente = conectar_google_sheets(creds_dict)
                    salvar_historico_online(cliente, SHEET_ID, usuario, prompt, resposta, imagem_envio.name)
                else:
                    st.warning("⚠️ Histórico não foi salvo (credenciais do Google ausentes).")

            except Exception as e:
                st.error(f"Erro: {e}")

# --- Histórico ---
elif menu == "Histórico":
    st.subheader("Histórico de Consultas")
    if creds_dict:
        try:
            cliente = conectar_google_sheets(creds_dict)
            historico = carregar_historico_online(cliente, SHEET_ID)

            senha_admin = st.sidebar.text_input("Senha de administrador", type="password")

            if senha_admin == st.secrets.get("ADMIN_PASS", "admin123"):
                st.success("✅ Acesso de administrador concedido.")
                for linha in historico[1:]:
                    st.markdown(f"**Data:** {linha[0]} | **Usuário:** {linha[1]}")
                    st.markdown(f"**Pergunta:** {linha[2]}")
                    st.markdown(f"**Resposta:** {linha[3]}")
                    st.markdown(f"**Imagem:** {linha[4]}")
                    st.markdown("---")
            else:
                usuario_filtro = st.text_input(
                    "Digite seu nome ou e-mail para ver seu histórico",
                    placeholder="Ex: joao@email.com"
                )
                if usuario_filtro:
                    historico_usuario = [linha for linha in historico[1:] if linha[1] == usuario_filtro]
                    if historico_usuario:
                        for linha in historico_usuario:
                            st.markdown(f"**Data:** {linha[0]}")
                            st.markdown(f"**Pergunta:** {linha[2]}")
                            st.markdown(f"**Resposta:** {linha[3]}")
                            st.markdown(f"**Imagem:** {linha[4]}")
                            st.markdown("---")
                    else:
                        st.info("Nenhuma consulta registrada ainda.")
                else:
                    st.warning("Digite seu nome ou e-mail para visualizar o histórico.")

        except Exception as e:
            st.error(f"Erro ao carregar histórico: {e}")
    else:
        st.warning("⚠️ Configure as credenciais do Google para salvar e visualizar o histórico.")
