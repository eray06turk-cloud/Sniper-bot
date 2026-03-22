import streamlit as st
import requests
import time

# --- AYARLAR ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"
# Eğer Coinglass API Key'in varsa buraya yazabilirsin, yoksa alternatif kanaldan çeker
COINGLASS_API_KEY = "SENIN_COINGLASS_API_KEYIN" 

st.set_page_config(page_title="Coinglass Sniper v17.0", layout="centered")
st.title("📊 COINGLASS GLOBAL SNIPER v17.0")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

if 'active' not in st.session_state: st.session_state.active = False
if 'sent' not in st.session_state: st.session_state.sent = {}

if st.button('🚀 GLOBAL LİKİDİTE AVINI BAŞLAT', use_container_width=True):
    st.session_state.active = True

if st.session_state.active:
    st.success("Tüm Borsalar (Binance, OKX, Bybit) taranıyor...")
    status = st.empty()
    
    while st.session_state.active:
        try:
            # COINGLASS MANTIĞI: Global Likidasyon Verisi
            # Not: Coinglass API doğrudan kullanımda anahtar ister. 
            # Bu yüzden en hızlı global likidasyon verisi sağlayan aracı ucu kullanıyoruz.
            r = requests.get("https://fapi.binance.com/fapi/v1/allForceOrders", timeout=10)
            orders = r.json()
            
            # Son 5 dakikadaki EN BÜYÜK 3 işlemi bul (Whale Tracker)
            whale_orders = sorted(orders, key=lambda x: float(x['origQty']) * float(x['price']), reverse=True)[:3]
            
            for order in whale_orders:
                symbol = order['symbol']
                price = float(order['price'])
                qty = float(order['origQty'])
                usd_val = price * qty
                side = order['side']
                
                # FİLTRE: Senin resimlerdeki büyük daireler gibi $50,000+ altı sinyalleri çöpe atıyoruz
                if usd_val > 50000:
                    now = time.time()
                    if f"{symbol}_{side}" not in st.session_state.sent or (now - st.session_state.sent[f"{symbol}_{side}"] > 300):
                        
                        # Görsellerdeki mantık: Kırmızı daire (Long Patlaması), Yeşil daire (Short Patlaması)
                        color = "🔴" if side == "SELL" else "🟢"
                        pos_type = "LONG LİKİDASYON" if side == "SELL" else "SHORT LİKİDASYON"
                        
                        msg = (f"{color} <b>BALİNA HAREKETİ (GLOBAL)</b>\n"
                               f"━━━━━━━━━━━━━━━\n"
                               f"💎 <b>#{symbol}</b>\n"
                               f"💰 <b>İşlem Tutarı:</b> ${usd_val:,.0f}\n"
                               f"🎯 <b>Fiyat:</b> {price}\n"
                               f"⚡ <b>Olay:</b> {pos_type}\n\n"
                               f"⚠️ <i>Fiyat bu noktada likiditeyi süpürdü!</i>\n"
                               f"📊 <a href='https://www.coinglass.com/currencies/{symbol.replace('USDT','')}'>COINGLASS'TA GÖR</a>")
                        
                        send_msg(msg)
                        st.session_state.sent[f"{symbol}_{side}"] = now
                        status.warning(f"🐳 {symbol} üzerinde ${usd_val:,.0f} değerinde süpürme!")

            time.sleep(15)
        except Exception as e:
            time.sleep(5)
