import streamlit as st
import requests
import time

# --- BİLGİLERİN ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"

st.set_page_config(page_title="Ultra Sniper v14.5", layout="centered")
st.title("🚀 ULTRA SNIPER V14.5")
st.subheader("Piyasa 5 Saniyede Bir Taranıyor...")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

if 'active' not in st.session_state: st.session_state.active = False
if 'sent' not in st.session_state: st.session_state.sent = {}

if st.button('🔥 TARAMAYI ŞİMDİ BAŞLAT', use_container_width=True):
    st.session_state.active = True

if st.session_state.active:
    st.success("Sistem Aktif! En ufak hareketi yakalıyorum...")
    log = st.empty()
    
    while st.session_state.active:
        try:
            # Binance'in en hızlı veri ucu
            r = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr", timeout=5)
            data = r.json()
            
            if not isinstance(data, list):
                time.sleep(2)
                continue

            for coin in data:
                symbol = coin.get('symbol', '')
                if symbol.endswith('USDT'):
                    # FİLTRELERİ MİNUMUMA ÇEKTİK (Hızlı sinyal için)
                    change = float(coin.get('priceChangePercent', 0))
                    vol = float(coin.get('quoteVolume', 0))
                    
                    # Filtre: %0.2 hareket ve 500k+ hacim (Çok hassas)
                    if abs(change) >= 0.2 and vol > 500000:
                        now = time.time()
                        # Aynı coini 5 dakikada bir at (Spam engelleme)
                        if symbol not in st.session_state.sent or (now - st.session_state.sent[symbol] > 300):
                            price = float(coin.get('lastPrice', 0))
                            side = "🟢 LONG" if change > 0 else "🔴 SHORT"
                            tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}PERP"
                            
                            msg = (f"<b>{side} SİNYALİ</b>\n"
                                   f"━━━━━━━━━━━━━━━\n"
                                   f"💎 <b>#{symbol}</b>\n"
                                   f"📈 Değişim: %{change:.2f}\n"
                                   f"💰 Fiyat: {price}\n"
                                   f"📊 <a href='{tv}'>GRAFİĞİ AÇ</a>")
                            
                            send_msg(msg)
                            st.session_state.sent[symbol] = now
                            log.info(f"Sinyal Gönderildi: {symbol} (%{change})")
            
            time.sleep(5) # 5 saniyede bir tarama (Hiper hız)
        except Exception as e:
            time.sleep(2)
