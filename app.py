import streamlit as st
import requests
import time

# --- AYARLAR ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"
LIQUIDITY_MULTIPLIER = 3.5  # Ortalama emrin 3.5 katı büyüklükteki emirleri yakala

st.set_page_config(page_title="Sniper v14.3 - Liquidity", layout="centered")
st.title("🎯 SNIPER V14.3 - LIQUIDITY HUNTER")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

if 'active' not in st.session_state: st.session_state.active = False
if 'sent' not in st.session_state: st.session_state.sent = {}

# Kontrol Paneli
c1, c2 = st.columns(2)
if c1.button('🚀 LİKİDİTE AVINI BAŞLAT'): st.session_state.active = True
if c2.button('🛑 DURDUR'): st.session_state.active = False

if st.session_state.active:
    st.warning("Balina emirleri ve Likidite duvarları taranıyor...")
    ph = st.empty()
    
    while st.session_state.active:
        try:
            # Önce aktif vadeli pariteleri al (İlk 20 pariteye odaklanalım hız için)
            ticker_resp = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr", timeout=10).json()
            # En yüksek hacimli ilk 30 coini filtrele (Likidite buralarda döner)
            top_coins = sorted([c for c in ticker_resp if c['symbol'].endswith('USDT')], 
                               key=lambda x: float(x['quoteVolume']), reverse=True)[:30]

            for coin in top_coins:
                symbol = coin['symbol']
                
                # EMİR DEFTERİ (ORDER BOOK) TARAMASI
                depth_url = f"https://fapi.binance.com/fapi/v1/depth?symbol={symbol}&limit=100"
                depth = requests.get(depth_url, timeout=5).json()
                
                bids = depth.get('bids', []) # Alış emirleri
                asks = depth.get('asks', []) # Satış emirleri

                if not bids or not asks: continue

                # Ortalama emir büyüklüğünü hesapla
                avg_bid = sum(float(b[1]) for b in bids) / len(bids)
                avg_ask = sum(float(a[1]) for a in asks) / len(asks)

                # BÜYÜK DUVAR TESPİTİ
                for b_price, b_qty in bids[:20]: # En yakın 20 fiyata bak
                    if float(b_qty) > avg_bid * LIQUIDITY_MULTIPLIER:
                        now = time.time()
                        if f"{symbol}_bid" not in st.session_state.sent or (now - st.session_state.sent[f"{symbol}_bid"] > 1800):
                            msg = (f"<b>🐋 BALİNA ALIŞ DUVARI (Mıknatıs)</b>\n"
                                   f"━━━━━━━━━━━━━━━\n"
                                   f"💎 <b>#{symbol}</b>\n"
                                   f"💰 <b>Destek/Hedef:</b> {b_price}\n"
                                   f"📊 <b>Emir Büyüklüğü:</b> {float(b_qty):.1f}\n"
                                   f"⚠️ Fiyat bu bölgeden sekerse LONG, süpürürse sert düşer!")
                            send_msg(msg)
                            st.session_state.sent[f"{symbol}_bid"] = now
                            ph.write(f"🐋 {symbol} Alış Duvarı Yakalandı!")

                for a_price, a_qty in asks[:20]:
                    if float(a_qty) > avg_ask * LIQUIDITY_MULTIPLIER:
                        now = time.time()
                        if f"{symbol}_ask" not in st.session_state.sent or (now - st.session_state.sent[f"{symbol}_ask"] > 1800):
                            msg = (f"<b>🐋 BALİNA SATIŞ DUVARI (Mıknatıs)</b>\n"
                                   f"━━━━━━━━━━━━━━━\n"
                                   f"💎 <b>#{symbol}</b>\n"
                                   f"💰 <b>Direnç/Hedef:</b> {a_price}\n"
                                   f"📊 <b>Emir Büyüklüğü:</b> {float(a_qty):.1f}\n"
                                   f"⚠️ Fiyat bu bölgeden sekerse SHORT, süpürürse sert çıkar!")
                            send_msg(msg)
                            st.session_state.sent[f"{symbol}_ask"] = now
                            ph.write(f"🐋 {symbol} Satış Duvarı Yakalandı!")

            time.sleep(30) # Tahtayı taramak zaman alır
        except:
            time.sleep(5)
