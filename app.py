import streamlit as st
import requests
import time

# --- AYARLAR ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"
PRICE_THRESHOLD = 0.5
MIN_VOLUME = 5000000

st.set_page_config(page_title="Sniper v14.2", layout="centered")
st.title("🎯 SNIPER ELITE V14.2")

# Telegram Gönderici
def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

if 'active' not in st.session_state: st.session_state.active = False
if 'sent' not in st.session_state: st.session_state.sent = {}

# Kontrol Butonları
c1, c2 = st.columns(2)
if c1.button('🚀 AVLANMAYA BAŞLA'): st.session_state.active = True
if c2.button('🛑 DURDUR'): st.session_state.active = False

if st.session_state.active:
    st.success("Sinyal avcısı aktif! Arka planda taranıyor...")
    ph = st.empty()
    
    while st.session_state.active:
        try:
            # Engel tanımayan hafif sorgu
            resp = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr", timeout=10)
            data = resp.json()
            
            # Eğer veri gelmezse akışı bozma
            if not isinstance(data, list):
                time.sleep(5)
                continue

            for coin in data:
                symbol = coin.get('symbol', '')
                if symbol.endswith('USDT'):
                    vol = float(coin.get('quoteVolume', 0))
                    
                    if vol > MIN_VOLUME:
                        change = float(coin.get('priceChangePercent', 0))
                        
                        if abs(change) >= PRICE_THRESHOLD:
                            now = time.time()
                            if symbol not in st.session_state.sent or (now - st.session_state.sent[symbol] > 900):
                                price = float(coin.get('lastPrice', 0))
                                high = float(coin.get('highPrice', 0))
                                low = float(coin.get('lowPrice', 0))
                                
                                # R1 / S1 Teknik Analiz
                                piv = (high + low + price) / 3
                                r1 = (2 * piv) - low
                                s1 = (2 * piv) - high
                                
                                side = "🟢 LONG" if change > 0 else "🔴 SHORT"
                                tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}PERP"
                                
                                msg = (f"<b>📊 SNIPER SIGNAL: {side}</b>\n"
                                       f"━━━━━━━━━━━━━━━\n"
                                       f"💎 <b>#{symbol}</b> | %{change:.2f}\n"
                                       f"💰 Fiyat: {price}\n"
                                       f"🚧 R1: {r1:.5g} | 🛡️ S1: {s1:.5g}\n\n"
                                       f"📊 <a href='{tv}'>GRAFİĞİ AÇ</a>")
                                
                                send_msg(msg)
                                st.session_state.sent[symbol] = now
                                ph.info(f"✅ Sinyal Gönderildi: {symbol} (%{change})")
            
            time.sleep(15) # 15 saniyede bir tazele
        except:
            time.sleep(5)
