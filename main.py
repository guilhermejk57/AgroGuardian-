import streamlit as st
from funcoes import processar_imagem, carregar_historico, salvar_historico
from PIL import Image

# --- Configurações do site ---
st.set_page_config(page_title="AgroGuardian - Detecção de Pragas", page_icon=":robot:", layout="centered")
st.title("🌱 AgroGuardian - Detecção de Pragas")
st.caption("Feito pelos alunos do 2°D Redes de Computadores")

# --- Carregar histórico global ---
if "historico" not in st.session_state:
    st.session_state.historico = carregar_historico()

# --- Flag para admin ---
if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# --- Entrada do usuário ---
consulta = st.text_input("Digite sua consulta:")
imagem = st.file_uploader("Envie uma imagem (opcional):", type=["jpg", "jpeg", "png"])

if st.button("Enviar"):
    if consulta.strip() == "" and imagem is None:
        st.warning("⚠️ Digite uma consulta ou envie uma imagem.")
    else:
        resposta = processar_imagem(consulta, imagem)

        # Salva no histórico da sessão
        st.session_state.historico.append({
            "consulta": consulta if consulta else "(sem texto)",
            "resposta": resposta
        })

        # Salva também em arquivo para persistência
        salvar_historico(st.session_state.historico)

# --- Exibe resultado da última consulta ---
if st.session_state.historico:
    st.subheader("📌 Última Resposta")
    st.write(st.session_state.historico[-1]["resposta"])

# --- ADMIN: ver histórico completo ---
with st.expander("🔑 Área do Criador"):
    if not st.session_state.admin_logado:
        senha = st.text_input("Digite a senha de admin:", type="password")
        if senha == st.secrets["admin"]["password"]:
            st.session_state.admin_logado = True
            st.success("✅ Acesso liberado! (sessão salva)")
        elif senha:
            st.error("❌ Senha incorreta!")
    else:
        st.success("✅ Você já está logado como admin.")
        if st.button("Sair da conta admin"):
            st.session_state.admin_logado = False
        else:
            for i, item in enumerate(st.session_state.historico, start=1):
                st.markdown(f"**{i}. Pergunta:** {item['consulta']}")
                st.markdown(f"**Resposta:** {item['resposta']}")
                st.markdown("---")
