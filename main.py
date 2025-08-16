import streamlit as st
import pandas as pd
from funcoes import processar_imagem, carregar_historico, salvar_historico

# --- Configuração inicial ---
st.set_page_config(page_title="AgroGuardian - Detecção de Pragas", page_icon="🌱", layout="centered")
st.title("🌱 AgroGuardian - Detecção de Pragas")
st.caption("Feito pelos alunos do 2°D Redes de Computadores")

# --- Histórico local ---
if "historico" not in st.session_state:
    st.session_state.historico = carregar_historico()

# --- Flag admin ---
if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# --- Entrada do usuário ---
consulta = st.text_input("Digite sua consulta:")
imagem = st.file_uploader("Envie uma imagem (opcional):", type=["jpg", "jpeg", "png"])

if st.button("Enviar"):
    if not consulta.strip() and imagem is None:
        st.warning("⚠️ Digite uma consulta ou envie uma imagem.")
    else:
        resposta = processar_imagem(consulta, imagem)

        # Salvar no histórico
        st.session_state.historico.append({
            "consulta": consulta if consulta else "(sem texto)",
            "resposta": resposta
        })
        salvar_historico(st.session_state.historico)

# --- Mostrar última resposta ---
if st.session_state.historico:
    st.subheader("📌 Última Resposta")
    st.write(st.session_state.historico[-1]["resposta"])

# --- Área Admin ---
with st.expander("🔑 Área do Criador"):
    if not st.session_state.admin_logado:
        senha = st.text_input("Digite a senha de admin:", type="password")
        if senha == st.secrets["admin"]["password"]:
            st.session_state.admin_logado = True
            st.success("✅ Acesso liberado!")
        elif senha:
            st.error("❌ Senha incorreta!")
    else:
        st.success("✅ Você está logado como admin.")
        if st.button("Sair da conta admin"):
            st.session_state.admin_logado = False
        else:
            # Mostrar histórico em tabela
            df = pd.DataFrame(st.session_state.historico)
            st.dataframe(df, use_container_width=True)

            # Botão para baixar CSV
            st.download_button(
                label="📥 Baixar histórico (CSV)",
                data=df.to_csv(index=False).encode("utf-8-sig"),
                file_name="historico.csv",
                mime="text/csv"
            )



