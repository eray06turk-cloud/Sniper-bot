import streamlit as st
import requests
import time

# --- AYARLAR ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"
VOLATILITY_THRESHOLD = 0.3  # Son 15 saniyede %0.3 ve üzeri ani hareketleri yakalar

st.set_page_config(page_title="Flash Sniper v14.4", layout="centered")
st.title("⚡ FLASH SNIPER V14.4")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

if 'active' not in st.session_state: st.session_state.active = False
if 'sent' not in st.session_state: st.session_state.sent = {}

c1, c2 = st.columns(2)
if c1.button('🚀 HIZLI TARAMAYI BAŞLAT'): st.session_state.active = True
if c2.button('🛑 DURDUR'): st.session_state.active = False

if st.session_state.active:
    st.success("Yüksek hızlı tarama devrede... Sinyal bekliyor.")
    ph = st.empty()
    
    while st.session_state.active:
        try:
            # Hafif ve hızlı veri çekme
            resp = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr", timeout=10)
            data = resp.json()
            
            if not isinstance(data, list):
                time.sleep(2)
                continue

            for coin in data:
                symbol = coin.get('symbol', '')
                if symbol.endswith('USDT'):
                    # Hacim filtresini biraz daha esnetelim ki daha fazla fırsat gelsin (1M+ yeterli)
                    if float(coin.get('quoteVolume', 0)) > 1000000:
                        change = float(coin.get('priceChangePercent', 0))
                        
                        # Anlık Patlama Kontrolü
                        if abs(change) >= 0.4: # En az %0.4 hareketli olanları listele
                            now = time.time()
                            if symbol not in st.session_state.sent or (now - st.session_state.sent[symbol] > 300): # 5 dakikada bir aynı coini at
                                price = float(coin.get('lastPrice', 0))
                                side = "🟢 HIZLI LONG" if change > 0 else "🔴 HIZLI SHORT"
                                tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}PERP"
                                
                                msg = (f"<b>⚡ FLASH SİNYAL: {side}</b>\n"
                                       f"━━━━━━━━━━━━━━━\n"
                                       f"💎 <b>#{symbol}</b>\n"
                                       f"📈 Değişim: %{change:.2f}\n"
                                       f"💰 Fiyat: {price}\n\n"
                                       f"📊 <a href='{tv}'>HEMEN GRAFİĞİ AÇ</a>")
                                
                                send_msg(msg)
                                st.session_state.sent[symbol] = now
                                ph.info(f"🔥 Sinyal Telegram'a Gönderildi: {symbol}")
            
            time.sleep(5) # Çok daha hızlı tara (5 saniye)
        except Exception as e:
            time.sleep(2)
