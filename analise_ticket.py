import yfinance as yf
import pandas_ta as ta
import pandas as pd
import os
import requests

# Carteira com os Tickers exatos para o Yahoo Finance ler os preços
ativos = [
    "VALE3.SA",
    "BBAS3.SA",
    "PETR3.SA",
    "ITSA4.SA",
    "WEGE3.SA",
    "EMBR3.SA",
    "POMO3.SA",
    "AXIA3.SA",
    "VGT",
    "KWEB",
    "TFLO",
    "GLD",
    "RSP",
    "BTC-USD",  # Código oficial do Bitcoin no Yahoo Finance
    "SOL-USD"   # Código oficial da Solana no Yahoo Finance
]

print("📊 Análise Técnica da Carteira\n")
relatorio = ""

for ativo in ativos:
    try:
        # 1. Baixar dados diários dos últimos 6 meses
        df = yf.download(ativo, period="6mo", progress=False)
        
        # Correção para novas versões do yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        # Pula o ativo se não retornou dados válidos
        if df.empty:
            print(f"Sem dados para {ativo}")
            continue
            
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
        
        # A) Tendência
        if ema20 > ema50:
            tendencia = "Alta 📈"
        else:
            tendencia = "Baixa 📉"
            
        # B) Ponto de Entrada
        if rsi < 30:
            entrada = "Ponto de Entrada (Sobrevendido) 🟢"
        elif rsi > 70:
            entrada = "Alerta: Sobrecomprado (Risco alto) 🔴"
        else:
            entrada = "Neutro ⚪"
            
        # C) Stop Loss de Volatilidade
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

print("Enviando relatório para o Telegram...")
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

url_tel = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Removido o parse_mode Markdown temporariamente para evitar falhas de envio
# caso algum número gere um caractere não reconhecido pelo Telegram
payload = {
    'chat_id': CHAT_ID,
    'text': relatorio
}

resposta_telegram = requests.post(url_tel, data=payload)

if resposta_telegram.status_code == 200:
    print("Relatório técnico enviado com sucesso!")
else:
    print(f"Erro ao enviar: {resposta_telegram.text}")
