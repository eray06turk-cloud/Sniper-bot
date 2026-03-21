import streamlit as st
import requests
import time

TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"

MIN_VOLUME = 10000000
PUMP_THRESHOLD = 2

st.title("🎯 SNIPER ELITE V15 (STABLE)")

if "running" not in st.session_state:
    st.session_state.running = False

if "sent" not in st.session_state:
    st.session_state.sent = {}

if "last_run" not in st.session_state:
    st.session_state.last_run = 0


def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.get(url, params=params)
    except:
        pass


col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 BAŞLAT"):
        st.session_state.running = True

with col2:
    if st.button("🛑 DURDUR"):
        st.session_state.running = False


if st.session_state.running:
    st.success("🟢 BOT AKTİF")
else:
    st.error("🔴 BOT DURDU")


if st.session_state.running:
    now = time.time()

    if now - st.session_state.last_run > 20:
        st.session_state.last_run = now

        try:
            # ✅ SPOT API (ENGEL YOK)
            url = "https://api.binance.com/api/v3/ticker/24hr"
            data = requests.get(url).json()

            if not isinstance(data, list):
                st.error(f"API Hatası: {data}")
                st.stop()

            for coin in data:
                symbol = coin['symbol']

                if not symbol.endswith("USDT"):
                    continue

                vol = float(coin['quoteVolume'])
                change = float(coin['priceChangePercent'])

                if vol < MIN_VOLUME:
                    continue

                if abs(change) < PUMP_THRESHOLD:
                    continue

                p = float(coin['lastPrice'])

                side = "🟢 LONG" if change > 0 else "🔴 SHORT"

                entry = p
                tp = p * 1.01 if change > 0 else p * 0.99
                sl = p * 0.99 if change > 0 else p * 1.01

                now_time = time.time()

                if symbol not in st.session_state.sent or (now_time - st.session_state.sent[symbol] > 900):

                    msg = (
                        f"📊 SNIPER SIGNAL\n"
                        f"💎 {symbol}\n"
                        f"%{change:.2f}\n\n"
                        f"{side}\n"
                        f"Entry: {entry}\n"
                        f"TP: {tp}\n"
                        f"SL: {sl}"
                    )

                    send_msg(msg)
                    st.session_state.sent[symbol] = now_time
                    st.write(f"✅ {symbol}")

        except Exception as e:
            st.error(f"Hata: {e}")