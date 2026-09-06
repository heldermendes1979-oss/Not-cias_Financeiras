import yfinance as yf
import pandas_ta as ta
import pandas as pd

# Carteira mista (Ações BR precisam do sufixo .SA, EUA/ETFs vão diretos, Cripto usa -USD)
ativos = [
    '"VALE3.SA" OR "Vale"',
    '"BBAS3.SA" OR "Banco do Brasil"',
    '"PETR3.SA" OR "Petrobras"',
    '"ITSA4.SA" OR "Itaúsa"',
    '"WEGE3.SA" OR "WEG"',
    '"EMBR3.SA" OR "Embraer"',
    '"POMO3.SA" OR "Marcopolo"',
    '"AXIA3.SA"',
    '"VGT" ETF',
    '"KWEB" ETF',
    '"TFLO" ETF',
    '"GLD" ouro',
    '"RSP" ETF',
    '"BITCOIN" criptomoeda',
    '"Solana" criptomoeda'
]

print("📊 Análise Técnica da Carteira\n")
relatorio = ""

for ativo in ativos:
    try:
        # 1. Baixar dados diários dos últimos 6 meses (necessário para calcular médias longas)
        df = yf.download(ativo, period="6mo", progress=False)
        
        # Correção para novas versões do yfinance que retornam colunas agrupadas
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        # 2. Calcular os indicadores matemáticos automaticamente na tabela
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.atr(length=14, append=True)
        
        # 3. Extrair os valores do dia mais recente
        ultimo_dia = df.iloc[-1]
        preco_atual = ultimo_dia['Close']
        ema20 = ultimo_dia['EMA_20']
        ema50 = ultimo_dia['EMA_50']
        rsi = ultimo_dia['RSI_14']
        atr = ultimo_dia['ATRr_14']
        
        # --- LÓGICA DE DECISÃO ---
        
        # A) Tendência (Curto prazo vs Médio prazo)
        if ema20 > ema50:
            tendencia = "Alta 📈"
        else:
            tendencia = "Baixa 📉"
            
        # B) Ponto de Entrada (RSI abaixo de 30 é sobrevenda, acima de 70 é sobrecompra)
        if rsi < 30:
            entrada = "Ponto de Entrada (Sobrevendido) 🟢"
        elif rsi > 70:
            entrada = "Alerta: Sobrecomprado (Risco alto) 🔴"
        else:
            entrada = "Neutro ⚪"
            
        # C) Stop Loss de Volatilidade (Preço - 2x a oscilação média diária)
        # O multiplicador 2 garante que você não seja "stopado" pelo ruído normal do dia a dia.
        stop_loss = preco_atual - (2 * atr)
        
        # --- FORMATAÇÃO DO TEXTO ---
        moeda = "R$" if ".SA" in ativo else "$"
        
        texto_ativo = (
            f"*{ativo.replace('.SA', '')}*\n"
            f"Preço: {moeda} {preco_atual:.2f}\n"
            f"Tendência: {tendencia}\n"
            f"Sinal: {entrada} (RSI: {rsi:.1f})\n"
            f"Stop Loss Técnico: {moeda} {stop_loss:.2f}\n"
            f"--------------------------\n"
        )
        
        print(texto_ativo)
        relatorio += texto_ativo
        
    except Exception as e:
        print(f"Erro ao processar {ativo}: {e}")

# Aqui você pode enviar a variável 'relatorio' para a API do Telegram igual fez no bot de notícias.
import os
import requests

# (Aqui fica todo aquele código de cálculo matemático do yfinance que mostrei antes)

print("Enviando relatório para o Telegram...")
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

url_tel = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {
    'chat_id': CHAT_ID,
    'text': relatorio, # A variável que guardou o texto de todos os ativos
    'parse_mode': 'Markdown'
}

resposta_telegram = requests.post(url_tel, data=payload)

if resposta_telegram.status_code == 200:
    print("Relatório técnico enviado com sucesso!")
else:
    print(f"Erro ao enviar: {resposta_telegram.text}")
