import streamlit as st
import requests
import time
import json
import websocket # Bunu kullanabilmek için terminale: pip install websocket-client yazmalısın

# --- AYARLAR ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"

st.title("🐋 THE WHALE EYE v15.0")
st.write("Canlı Emir Akışı ve Likidite Süpürme Avcısı Aktif...")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

# --- STRATEJİ: AGRESİF EMİR TAKİBİ ---
# Burada sadece büyük 'Market' emirlerini ve likidite boşaltmalarını yakalıyoruz.
def on_message(ws, message):
    data = json.loads(message)
    # Veri formatı: Binance Liquidation Feed veya AggTrade
    symbol = data['s']
    side = data['S']
    price = data['p']
    quantity = data['q']
    usd_val = float(price) * float(quantity)
    
    # EĞER 50.000$ ÜZERİ BİR LİKİDİTE SÜPÜRMESİ VARSA (Giriş Fırsatı)
    if usd_val > 50000:
        msg = (f"<b>🔥 LİKİDİTE SÜPÜRÜLDÜ (SWEEP)!</b>\n"
               f"━━━━━━━━━━━━━━━\n"
               f"💎 <b>#{symbol}</b>\n"
               f"🧭 <b>Yön:</b> {'🔴 LONG PATLADI (SHORT FIRSATI)' if side == 'SELL' else '🟢 SHORT PATLADI (LONG FIRSATI)'}\n"
               f"💰 <b>Miktar:</b> ${usd_val:,.0f}\n"
               f"🎯 <b>Fiyat:</b> {price}\n\n"
               f"⚠️ Balinalar likiditeyi temizledi, ters yöne sert hareket gelebilir!")
        send_msg(msg)

# --- SİSTEMİ BAŞLAT ---
if st.button('🐋 BALİNA AVINI BAŞLAT'):
    st.info("Binance Canlı Akışına Bağlanılıyor... (Liquidation Stream)")
    # Binance'in en hızlı 'Liquidation' (Likidite patlama) kanalına bağlanıyoruz
    ws_url = "wss://fstream.binance.com/ws/!forceOrder@arr"
    
    def run_ws():
        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        ws.run_forever()

    import threading
    thread = threading.Thread(target=run_ws)
    thread.start()
    st.success("Canlı takip başladı! Telegram'ı bekle.")
