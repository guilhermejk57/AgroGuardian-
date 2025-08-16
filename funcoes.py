import json
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

def carregar_culturas():
    """Carrega a base de conhecimento de culturas e pragas"""
    with open('culturas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def resposta_gemini(modelo, imagem, prompt):
    """Envia imagem + pergunta para o modelo Gemini"""
    contexto_agro = """
Você é um chatbot especializado em detecção, identificação e controle de pragas urbanas, agrícolas e domésticas.
Responda apenas perguntas relacionadas a esse tema, como: tipos de pragas, formas de controle, prevenção, identificação de sinais, uso de pesticidas, métodos naturais e outras dúvidas específicas sobre infestação e manejo.
Se o usuário fizer uma pergunta fora desse escopo, recuse educadamente.
Mantenha um tom profissional e acessível.
    """
    resposta = modelo.generate_content([imagem[0], contexto_agro + prompt])
    return resposta.text

def imagem2bytes(imagem_upload):
    """Converte a imagem enviada para bytes antes de enviar ao modelo"""
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

def conectar_google(creds_dict):
    """Conecta Google Sheets + Drive"""
    escopos = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=escopos)
    cliente_sheets = gspread.authorize(creds)
    cliente_drive = build("drive", "v3", credentials=creds)
    return cliente_sheets, cliente_drive

def upload_imagem_drive(imagem_upload, cliente_drive, pasta_id):
    """Faz upload da imagem no Google Drive (pasta compartilhada) e retorna link público"""
    file_metadata = {
        "name": imagem_upload.name,
        "mimeType": imagem_upload.type,
        "parents": [pasta_id]  # salva dentro da pasta
    }
    media = MediaIoBaseUpload(io.BytesIO(imagem_upload.getvalue()), mimetype=imagem_upload.type)

    arquivo = cliente_drive.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    # Tornar arquivo público
    cliente_drive.permissions().create(
        fileId=arquivo["id"],
        body={"role": "reader", "type": "anyone"}
    ).execute()

    return f"https://drive.google.com/uc?id={arquivo['id']}"

def salvar_historico_online(usuario, pergunta, resposta, imagem_upload, sheet_id, creds_dict, pasta_id):
    """Salva nova linha no histórico da planilha, com link da imagem"""
    cliente_sheets, cliente_drive = conectar_google(creds_dict)
    planilha = cliente_sheets.open_by_key(sheet_id)
    aba = planilha.sheet1

    link_imagem = upload_imagem_drive(imagem_upload, cliente_drive, pasta_id)

    aba.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        usuario,
        pergunta,
        resposta,
        link_imagem
    ])

def carregar_historico_online(sheet_id, creds_dict):
    """Carrega todas as linhas do histórico"""
    cliente_sheets, _ = conectar_google(creds_dict)
    planilha = cliente_sheets.open_by_key(sheet_id)
    aba = planilha.sheet1
    return aba.get_all_values()
