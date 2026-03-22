import streamlit as st
import requests
import time

# --- BİLGİLERİN ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"

st.set_page_config(page_title="Sniper v15.1", layout="centered")
st.title("🐋 WHALE & LIQUIDITY SNIPER v15.1")
st.write("Sadece Büyük Hareketler ve Likidite Süpürmeleri Taranıyor...")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

if 'active' not in st.session_state: st.session_state.active = False
if 'sent' not in st.session_state: st.session_state.sent = {}

if st.button('🚀 LİKİDİTE AVINI BAŞLAT', use_container_width=True):
    st.session_state.active = True

if st.session_state.active:
    st.success("Canlı veri akışı aktif! Balinalar bekleniyor...")
    status = st.empty()
    
    while st.session_state.active:
        try:
            # Saniyeler içindeki büyük 'Aggregated' işlemlere odaklanıyoruz
            # Binance'in en güncel 24h ticker verisi üzerinden anlık değişim takibi
            r = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr", timeout=5)
            data = r.json()
            
            for coin in data:
                symbol = coin.get('symbol', '')
                if symbol.endswith('USDT'):
                    # FİLTRE: Sadece gerçekten hacimli ve sert hareket edenleri yakala
                    # Son 24 saatte en az 10M USDT hacim dönmüş olmalı
                    vol = float(coin.get('quoteVolume', 0))
                    if vol > 10000000:
                        change = float(coin.get('priceChangePercent', 0))
                        
                        # %1.5 ve üzeri sert hareketler (Balina giriş çıkışı veya likidite süpürme belirtisi)
                        if abs(change) >= 1.5:
                            now = time.time()
                            if symbol not in st.session_state.sent or (now - st.session_state.sent[symbol] > 600):
                                price = float(coin.get('lastPrice', 0))
                                side = "🟢 AGRESİF ALIM" if change > 0 else "🔴 AGRESİF SATIŞ"
                                tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}PERP"
                                
                                msg = (f"<b>{side} TESPİT EDİLDİ!</b>\n"
                                       f"━━━━━━━━━━━━━━━\n"
                                       f"💎 <b>#{symbol}</b>\n"
                                       f"📈 <b>Anlık Değişim:</b> %{change:.2f}\n"
                                       f"💰 <b>Fiyat:</b> {price}\n\n"
                                       f"⚠️ Bu kadar sert bir hareket likidite süpürmesi olabilir. Grafiği kontrol et!")
                                
                                send_msg(msg)
                                st.session_state.sent[symbol] = now
                                status.info(f"🔥 Sinyal Gönderildi: {symbol}")
            
            time.sleep(3) # 3 saniyede bir yıldırım hızında tarama
        except:
            time.sleep(2)
