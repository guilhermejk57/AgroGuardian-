import json
import csv
from datetime import datetime

def carregar_culturas():
    """Carrega a base de conhecimento de culturas e pragas"""
    with open('culturas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def resposta_gemini(modelo, imagem, prompt):
    """
    Recebe a imagem, o prompt e retorna o que o usuário pediu com contexto agrícola.
    """
    contexto_agro = """
Você é um chatbot especializado em detecção, identificação e controle de pragas urbanas, agrícolas e domésticas.
Responda apenas perguntas relacionadas a esse tema, como: tipos de pragas, formas de controle, prevenção, identificação de sinais, uso de pesticidas, métodos naturais e outras dúvidas específicas sobre infestação e manejo.
Se o usuário fizer uma pergunta fora desse escopo (por exemplo, sobre saúde humana, finanças, tecnologia ou qualquer outro assunto), recuse educadamente dizendo: "Desculpe, minha função é apenas ajudar com assuntos relacionados à detecção e controle de pragas. Posso te ajudar com alguma dúvida sobre isso?"
Não responda perguntas que não estejam diretamente ligadas ao tema.
Mantenha um tom profissional e acessível, adequado tanto para produtores rurais quanto para o público em geral.
    """
    resposta = modelo.generate_content([imagem[0], contexto_agro + prompt])
    return resposta.text

def imagem2bytes(imagem_upload):
    """
    Converte a imagem enviada para bytes no formato aceito pela API Gemini.
    """
    if imagem_upload is not None:
        if imagem_upload.size > 5 * 1024 * 1024:
            raise ValueError("Imagem muito grande! Tamanho máximo: 5MB.")

        imagem_bytes = imagem_upload.getvalue()
        partes_imagem = [{
            'mime_type': imagem_upload.type,
            'data': imagem_bytes
        }]
        return partes_imagem
    else:
        raise FileNotFoundError('Nenhuma imagem foi carregada.')

def salvar_historico(pergunta, resposta, nome_imagem):
    """Salva as consultas em um arquivo CSV"""
    with open('historico.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pergunta, resposta, nome_imagem])
