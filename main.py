
import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

def analyze_position(symbol: str) -> str:
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval=3m&limit=3"
    try:
        response = requests.get(url)
        data = response.json()
        logging.info(f"Binance API 응답: {data}")

        if not data or not isinstance(data, list):
            return "데이터를 불러올 수 없습니다. (빈 응답)"

        closes = [float(candle[4]) for candle in data if len(candle) > 4]

        if len(closes) < 2:
            return f"캔들 데이터가 부족합니다. (수신된 종가 수: {len(closes)})"

        if closes[-1] > closes[0]:
            return "롱"
        elif closes[-1] < closes[0]:
            return "숏"
        else:
            return "횡보"
    except Exception as e:
        logging.error(f"에러 발생: {e}")
        return f"에러 발생: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 코인 포지션 분석 봇입니다. 예: /position BTC")

async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("코인 심볼을 입력해주세요. 예: /position BTC")
        return

    input_symbol = context.args[0].upper()
    if not input_symbol.endswith("USDT"):
        symbol = input_symbol + "USDT"
    else:
        symbol = input_symbol

    result = analyze_position(symbol)
    await update.message.reply_text(f"{symbol} 포지션: {result}")

# 메인 루프 직접 실행
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("position", position))
app.run_polling()
