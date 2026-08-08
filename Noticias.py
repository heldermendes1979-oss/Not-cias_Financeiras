!pip install feedparser google-generativeai

import os
import requests
import feedparser
import google.generativeai as genai
import urllib.parse # Import urllib.parse for URL encoding

# 1. Carregar chaves de API (GitHub Secrets)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# 2. Definir os temas e a sua carteira consolidada
temas_macro = ["Macroeconomia Brasil", "Juros Federal Reserve EUA", "Inflação"]

# Carteira estruturada com operadores de busca para evitar ruídos
carteira = [
    # Ações BR
    '"VALE3" OR "Vale"',
    '"BBAS3" OR "Banco do Brasil"',
    '"PETR3" OR "Petrobras"',
    '"ITSA4" OR "Itaúsa"',
    '"WEGE3" OR "WEG"',
    '"EMBR3" OR "Embraer"',
    '"POMO3" OR "Marcopolo"',
    '"AXIA3"',
    '"GGBR4" OR "Gerdau"',
    '"RAIZ4" OR "Raízen"',

    # Exterior, ETFs e Cripto
    '"VGT" ETF',
    '"KWEB" ETF',
    '"TFLO" ETF',
    '"BLOK" ETF',
    '"GLD" ouro',
    '"RITM" mercado financeiro',
    '"ARLP" stocks',
    '"Copper ETF" OR "ETF de Cobre"',
    '"Solana" criptomoeda'
]

def buscar_noticias(termo):
    # Busca notícias das últimas 24h via Google News RSS
    encoded_termo = urllib.parse.quote_plus(termo) # URL-encode the search term
    url = f"https://news.google.com/rss/search?q={encoded_termo}+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(url)
    # Pega apenas as 3 principais notícias de cada termo
    return [entry.title for entry in feed.entries[:3]]

print("Coletando notícias...")
texto_bruto = "Notícias coletadas hoje:\n"

for item in temas_macro + carteira:
    manchetes = buscar_noticias(item)
    if manchetes:
        texto_bruto += f"\n- {item}:\n" + "\n".join(f"  * {m}" for m in manchetes)

print("Gerando resumo com IA...")
# 3. Enviar para o Gemini resumir
model = genai.GenerativeModel('gemini-1.5-flash')
prompt = f"""
Você é um analista financeiro. Leia as manchetes abaixo e crie um boletim matinal executivo, curto e direto em português.
Divida o boletim em duas seções usando Markdown:
1. 🌍 Macroeconomia (Destaques de Brasil e EUA)
2. 💼 Radar da Carteira (O que aconteceu com os ativos específicos)

Foque apenas no que é relevante, como pagamentos de dividendos, balanços e fatos relevantes.
Se não houver notícia para um ativo, ignore-o e não o mencione no resumo.

Notícias brutas:
{texto_bruto}
"""

resposta = model.generate_content(prompt)
resumo_final = resposta.text

print("Enviando para o Telegram...")
# 4. Enviar mensagem para o Telegram
url_tel = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {
    'chat_id': CHAT_ID,
    'text': resumo_final,
    'parse_mode': 'Markdown'
}
requests.post(url_tel, data=payload)
print("Processo concluído com sucesso!")
