import os
import requests
import feedparser
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai

# 1. Carregar chaves de API
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
EMAIL_DESTINO = 'heldermendes1979@gmail.com'

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

# 2. Definir os temas e carteira
temas_macro = ["Macroeconomia Brasil", "Juros Federal Reserve EUA", "Inflação"]
carteira = [
    '"VALE3" OR "Vale"',
    '"BBAS3" OR "Banco do Brasil"',
    '"PETR3" OR "Petrobras"',
    '"ITSA4" OR "Itaúsa"',
    '"WEGE3" OR "WEG"',
    '"EMBR3" OR "Embraer"',
    '"POMO3" OR "Marcopolo"',
    '"AXIA3"',
    '"VGT" ETF',
    '"KWEB" ETF',
    '"TFLO" ETF',
    '"GLD" ouro',
    '"RSP" ETF',
    '"BITCOIN" criptomoeda',
    '"Solana" criptomoeda'
]

def buscar_noticias(termo):
    termo_seguro = urllib.parse.quote(termo)
    url = f"https://news.google.com/rss/search?q={termo_seguro}+when:1d&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(url)
    return [entry.title for entry in feed.entries[:3]]

print("Coletando notícias...")
texto_bruto = "Notícias coletadas hoje:\n"

for item in temas_macro + carteira:
    manchetes = buscar_noticias(item)
    if manchetes:
        texto_bruto += f"\n- {item}:\n" + "\n".join(f"  * {m}" for m in manchetes)

print("Gerando resumo com IA...")
prompt = f"""
Você é um analista financeiro. Leia as manchetes abaixo e crie um boletim matinal executivo, curto e direto em português.
Divida o boletim em duas seções:
1. Macroeconomia (Destaques de Brasil e EUA)
2. Radar da Carteira (O que aconteceu com os ativos específicos)

Foque apenas no que é relevante, como pagamentos de dividendos, balanços e fatos relevantes. 
Se não houver notícia para um ativo, ignore-o e não o mencione no resumo.

Notícias brutas:
{texto_bruto}
"""

resposta = client.models.generate_content(
    model='gemini-3.6-flash',  # Atualizado para o modelo mais recente e estável
    contents=prompt
)
resumo_final = resposta.text
print("Resumo gerado!")

# 3. Enviar para o Telegram
print("Enviando para o Telegram...")
url_tel = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {'chat_id': CHAT_ID, 'text': resumo_final}
resp_tel = requests.post(url_tel, data=payload)
if resp_tel.status_code == 200:
    print("Telegram: Enviado com sucesso!")
else:
    print(f"Erro Telegram: {resp_tel.text}")

# 4. Enviar para o E-mail
print("Enviando para o e-mail...")
try:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_DESTINO
    msg['Subject'] = 'Boletim Financeiro Diário'
    
    # Adiciona o texto do resumo no corpo do e-mail
    msg.attach(MIMEText(resumo_final, 'plain'))
    
    # Conecta ao servidor do Gmail e envia
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, EMAIL_DESTINO, msg.as_string())
    server.quit()
    print("E-mail: Enviado com sucesso!")
except Exception as e:
    print(f"Erro E-mail: {e}")

print("Processo finalizado!")
