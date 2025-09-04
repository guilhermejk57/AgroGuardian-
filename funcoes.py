import json
from datetime import datetime
from zoneinfo import ZoneInfo  # fuso horário Brasil
import gspread
from google.oauth2.service_account import Credentials


# --- Carregar culturas do JSON ---
def carregar_culturas():
    with open("culturas.json", "r", encoding="utf-8") as f:
        return json.load(f)


# --- Chamar Gemini com contexto ---
def resposta_gemini(modelo, imagem, prompt):
    contexto = """
    Você é um especialista em pragas agrícolas. Sua tarefa é analisar imagens de plantas
    e identificar possíveis pragas ou doenças, sempre respondendo de forma técnica,
    concisa e profissional. Se a dúvida não estiver relacionada a agricultura ou pragas,
    recuse respondendo educadamente.
    """
    resposta = modelo.generate_content([imagem[0], contexto + prompt])
    return resposta.text


# --- Converter imagem para bytes ---
def imagem2bytes(imagem_upload):
    if not imagem_upload:
        raise ValueError("Nenhuma imagem enviada.")
    if imagem_upload.size > 5 * 1024 * 1024:
        raise ValueError("Imagem muito grande! Máximo permitido é 5MB.")
    bytes_img = imagem_upload.getvalue()
    return [{"mime_type": imagem_upload.type, "data": bytes_img}]


# --- Conectar ao Google Sheets ---
def conectar_google_sheets(creds_dict):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


# --- Salvar histórico online ---
def salvar_historico_online(cliente, sheet_id, usuario, pergunta, resposta, nome_arquivo):
    planilha = cliente.open_by_key(sheet_id)
    aba = planilha.sheet1

    # horário corrigido para fuso Brasil
    data_hora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")

    aba.append_row([data_hora, usuario, pergunta, resposta, nome_arquivo])


# --- Carregar histórico online ---
def carregar_historico_online(cliente, sheet_id):
    planilha = cliente.open_by_key(sheet_id)
    aba = planilha.sheet1
    return aba.get_all_values()


