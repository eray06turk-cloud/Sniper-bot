import streamlit as st
import requests
import time

# --- AYARLAR (GOMULU) ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"
PRICE_THRESHOLD = 0.5   # %0.5 hareket eşiği
MIN_VOLUME = 5000000    # 5M+ USDT Hacim filtresi

st.set_page_config(page_title="Sniper Elite v14.1", layout="centered")
st.title("🎯 SNIPER ELITE V14.1")
st.info("Sistem 7/24 Aktif - Sinyaller Doğrudan Telegram'a Gönderilir.")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID, 
            "text": text, 
            "parse_mode": "HTML", 
            "disable_web_page_preview": "true"
        }
        requests.get(url, params=params, timeout=10)
    except Exception as e:
        st.error(f"Telegram Hatası: {e}")

if 'sent' not in st.session_state:
    st.session_state.sent = {}

# Arayüz Butonları
col1, col2 = st.columns(2)
with col1:
    start_btn = st.button('🚀 AVLANMAYA BAŞLA', use_container_width=True)
with col2:
    stop_btn = st.button('🛑 DURDUR', use_container_width=True)

if start_btn:
    st.success("Tarama Başlatıldı! Piyasa taranıyor...")
    placeholder = st.empty()
    
    while True:
        try:
            # Binance Vadeli İşlemler Verisi
            r = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr", timeout=15)
            data = r.json()
            
            if not isinstance(data, list):
                st.warning("Veri bekleniyor... (Binance kısıtlaması)")
                time.sleep(10)
                continue

            for coin in data:
                symbol = coin.get('symbol', '')
                if symbol.endswith('USDT'):
                    vol = float(coin.get('quoteVolume', 0))
                    
                    # 5M+ Hacim Filtresi
                    if vol > MIN_VOLUME:
                        change = float(coin.get('priceChangePercent', 0))
                        
                        # %0.5 Değişim Eşiği
                        if abs(change) >= PRICE_THRESHOLD:
                            now = time.time()
                            # 15 dakika spam engelleme
                            if symbol not in st.session_state.sent or (now - st.session_state.sent[symbol] > 900):
                                price = float(coin.get('lastPrice', 0))
                                high = float(coin.get('highPrice', 0))
                                low = float(coin.get('lowPrice', 0))
                                
                                # Profesyonel Teknik Analiz (R1 / S1)
                                piv = (high + low + price) / 3
                                r1 = (2 * piv) - low
                                s1 = (2 * piv) - high
                                
                                side = "🟢 LONG" if change > 0 else "🔴 SHORT"
                                tv_link = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}PERP"
                                
                                msg = (f"<b>📊 SNIPER SIGNAL: {side}</b>\n"
                                       f"━━━━━━━━━━━━━━━\n"
                                       f"💎 <b>#{symbol}</b> | %{change:.2f}\n"
                                       f"💰 Fiyat: {price}\n"
                                       f"🚧 R1: {r1:.5g}\n"
                                       f"🛡️ S1: {s1:.5g}\n\n"
                                       f"📊 <a href='{tv_link}'>GRAFİĞİ AÇ</a>")
                                
                                send_msg(msg)
                                st.session_state.sent[symbol] = now
                                placeholder.write(f"✅ Sinyal Gönderildi: {symbol} (%{change})")
            
            time.sleep(20) # 20 saniyede bir tarama
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
            time.sleep(10)
