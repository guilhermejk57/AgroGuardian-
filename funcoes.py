import streamlit as st
import google.generativeai as genai
import json
import os

HISTORICO_ARQUIVO = "historico.json"

# --- Configurar API Gemini ---
genai.configure(api_key=st.secrets["gemini"]["api_key"])

# --- Função para processar imagem/texto ---
def processar_imagem(consulta, imagem):
    modelo = genai.GenerativeModel("gemini-1.5-flash")

    if imagem:
        conteudo = [
            {"mime_type": "image/jpeg", "data": imagem.read()},
            {"text": consulta if consulta else "Descreva a imagem"}
        ]
        resposta = modelo.generate_content(conteudo)
        return resposta.text
    else:
        resposta = modelo.generate_content(consulta)
        return resposta.text

# --- Salvar histórico em arquivo JSON ---
def salvar_historico(historico):
    with open(HISTORICO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

# --- Carregar histórico do arquivo JSON ---
def carregar_historico():
    if os.path.exists(HISTORICO_ARQUIVO):
        with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
