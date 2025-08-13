import json
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

def carregar_culturas():
    """Carrega a base de conhecimento de culturas e pragas"""
    with open('culturas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def resposta_gemini(modelo, imagem, prompt):
    contexto_agro = """
Você é um chatbot especializado em detecção, identificação e controle de pragas urbanas, agrícolas e domésticas.
Responda apenas perguntas relacionadas a esse tema, como: tipos de pragas, formas de controle, prevenção, identificação de sinais, uso de pesticidas, métodos naturais e outras dúvidas específicas sobre infestação e manejo.
Se o usuário fizer uma pergunta fora desse escopo, recuse educadamente.
Mantenha um tom profissional e acessível.
    """
    resposta = modelo.generate_content([imagem[0], contexto_agro + prompt])
    return resposta.text

def imagem2bytes(imagem_upload):
    if imagem_upload is not None:
        if imagem_upload.size > 5 * 1024 * 1024:
            raise ValueError("Imagem muito grande! Máximo 5MB.")
        imagem_bytes = imagem_upload.getvalue()
        partes_imagem = [{
            'mime_type': imagem_upload.type,
            'data': imagem_bytes
        }]
        return partes_imagem
    else:
        raise FileNotFoundError('Nenhuma imagem foi carregada.')

def conectar_google_sheets(creds_dict):
    escopos = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=escopos)
    cliente = gspread.authorize(creds)
    return cliente

def salvar_historico_online(pergunta, resposta, nome_imagem, sheet_id, creds_dict):
    cliente = conectar_google_sheets(creds_dict)
    planilha = cliente.open_by_key(sheet_id)
    aba = planilha.sheet1
    aba.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        pergunta,
        resposta,
        nome_imagem
    ])

def carregar_historico_online(sheet_id, creds_dict):
    cliente = conectar_google_sheets(creds_dict)
    planilha = cliente.open_by_key(sheet_id)
    aba = planilha.sheet1
    return aba.get_all_values()
