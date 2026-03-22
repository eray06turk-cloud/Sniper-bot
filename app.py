import streamlit as st
import requests
import time

# --- AYARLAR ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"

st.set_page_config(page_title="Global Sniper v14.6", layout="centered")
st.title("🌐 GLOBAL DATA SNIPER V14.6")
st.write("Veri Kaynağı: Global Price Aggregator (Engelsiz)")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

if 'active' not in st.session_state: st.session_state.active = False
if 'sent' not in st.session_state: st.session_state.sent = {}

if st.button('🚀 ALTERNATİF TARAMAYI BAŞLAT', use_container_width=True):
    st.session_state.active = True

if st.session_state.active:
    st.success("Alternatif veri kanalı aktif! Sinyaller bekleniyor...")
    status = st.empty()
    
    while st.session_state.active:
        try:
            # Binance yerine CryptoCompare API (Engellenmesi çok zor, stabil veri)
            # Ücretsiz ve anahtarsız hızlı veri çekme
            url = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC,ETH,SOL,BNB,XRP,ADA,DOGE,AVAX,TRX,LINK,DOT,MATIC,LTC,SHIB,NEAR,PEOPLE,1000SHIB,BONK,MEME&tsyms=USDT"
            r = requests.get(url, timeout=10)
            res = r.json()
            
            if "RAW" in res:
                raw_data = res["RAW"]
                for coin in raw_data:
                    symbol = f"{coin}USDT"
                    details = raw_data[coin]["USDT"]
                    
                    change = float(details["CHANGEPCT24HOUR"]) # 24 saatlik yüzde
                    price = float(details["PRICE"])
                    vol = float(details["VOLUME24HOURTO"]) # USDT Hacmi
                    
                    # Filtre: %0.3 hareket ve hacim
                    if abs(change) >= 0.3:
                        now = time.time()
                        if symbol not in st.session_state.sent or (now - st.session_state.sent[symbol] > 600):
                            side = "🟢 LONG" if change > 0 else "🔴 SHORT"
                            tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}PERP"
                            
                            msg = (f"<b>{side} (Global Data)</b>\n"
                                   f"━━━━━━━━━━━━━━━\n"
                                   f"💎 <b>#{symbol}</b>\n"
                                   f"📈 Değişim: %{change:.2f}\n"
                                   f"💰 Fiyat: {price}\n"
                                   f"📊 <a href='{tv}'>GRAFİĞİ AÇ</a>")
                            
                            send_msg(msg)
                            st.session_state.sent[symbol] = now
                            status.info(f"Sinyal Gönderildi: {symbol}")
            
            time.sleep(15) # Global veri 15 saniyede bir güncellenir
        except Exception as e:
            status.error(f"Veri çekme hatası: {e}")
            time.sleep(5)
