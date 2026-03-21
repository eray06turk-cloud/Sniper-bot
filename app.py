import streamlit as st
import requests
import time

# --- AYARLAR ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"

MIN_VOLUME = 15000000
PUMP_THRESHOLD = 2

st.set_page_config(page_title="SNIPER ELITE V15 PRO", layout="wide")

st.title("🎯 SNIPER ELITE V15 PRO")
st.write("Pump / Dump yakalama sistemi aktif")

# SESSION
if "running" not in st.session_state:
    st.session_state.running = False

if "sent" not in st.session_state:
    st.session_state.sent = {}

if "last_run" not in st.session_state:
    st.session_state.last_run = 0


# TELEGRAM
def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true"
        }
        requests.get(url, params=params, timeout=5)
    except:
        pass


# BUTONLAR
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 BAŞLAT"):
        st.session_state.running = True

with col2:
    if st.button("🛑 DURDUR"):
        st.session_state.running = False


# DURUM
if st.session_state.running:
    st.success("🟢 BOT AKTİF")
else:
    st.error("🔴 BOT DURDU")


# ANA TARAYICI
if st.session_state.running:
    now = time.time()

    if now - st.session_state.last_run > 20:
        st.session_state.last_run = now

        try:
            r = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr", timeout=10)
            data = r.json()

            # HATA KORUMA
            if not isinstance(data, list):
                st.error(f"API Hatası: {data}")
                time.sleep(5)
                st.stop()

            for coin in data:

                if not isinstance(coin, dict):
                    continue

                symbol = coin.get('symbol', '')

                if not symbol.endswith("USDT"):
                    continue

                vol = float(coin.get('quoteVolume', 0))
                change = float(coin.get('priceChangePercent', 0))

                if vol < MIN_VOLUME:
                    continue

                # LONG
                if change > PUMP_THRESHOLD:
                    p = float(coin['lastPrice'])
                    h = float(coin['highPrice'])

                    if p > h * 0.98:
                        side = "🟢 LONG"
                        entry = p
                        tp = p * 1.01
                        sl = p * 0.99
                    else:
                        continue

                # SHORT
                elif change < -PUMP_THRESHOLD:
                    p = float(coin['lastPrice'])
                    l = float(coin['lowPrice'])

                    if p < l * 1.02:
                        side = "🔴 SHORT"
                        entry = p
                        tp = p * 0.99
                        sl = p * 1.01
                    else:
                        continue
                else:
                    continue

                now_time = time.time()

                if symbol not in st.session_state.sent or (now_time - st.session_state.sent[symbol] > 900):

                    tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}PERP"

                    msg = (
                        f"<b>📊 SNIPER PRO SIGNAL</b>\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"💎 <b>{symbol}</b>\n"
                        f"📈 Değişim: %{change:.2f}\n\n"
                        f"{side}\n"
                        f"🎯 Entry: {entry}\n"
                        f"🏆 TP: {tp}\n"
                        f"🛑 SL: {sl}\n\n"
                        f"📊 <a href='{tv}'>Grafiği Aç</a>"
                    )

                    send_msg(msg)
                    st.session_state.sent[symbol] = now_time

                    st.write(f"✅ Sinyal: {symbol}")

        except Exception as e:
            st.error(f"Hata: {e}")