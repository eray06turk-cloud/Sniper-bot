import streamlit as st
import requests
import time

# --- AYARLAR ---
TELEGRAM_TOKEN = "8775179244:AAEXxd5pN2CXtqp67jRDeVDj8OQrGpXoExc"
CHAT_ID = "8680241935"

st.set_page_config(page_title="Siren Hunter v16.0", layout="centered")
st.title("🚨 SIREN HUNTER v16.0")
st.subheader("Likidite Süpürme ve Balina Emirleri Takibi")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"}
        requests.get(url, params=params, timeout=5)
    except: pass

if 'active' not in st.session_state: st.session_state.active = False
if 'sent' not in st.session_state: st.session_state.sent = {}

if st.button('🔥 LİKİDİTE AVINI BAŞLAT', use_container_width=True):
    st.session_state.active = True

if st.session_state.active:
    st.success("Coinglass Tarzı Canlı Likidite Taraması Başlatıldı...")
    placeholder = st.empty()
    
    while st.session_state.active:
        try:
            # 1. ADIM: Binance Likidasyon Akışını ve Büyük Emirleri Yakala
            # Bu API ucu son likidasyonları (patlayan pozisyonları) getirir
            r = requests.get("https://fapi.binance.com/fapi/v1/allForceOrders", timeout=10)
            data = r.json()
            
            if data and isinstance(data, list):
                # En son gerçekleşen büyük likidasyonlara bak
                for order in data[-10:]:  # Son 10 büyük patlama
                    symbol = order.get('symbol')
                    side = order.get('side')
                    price = float(order.get('price'))
                    qty = float(order.get('origQty'))
                    usd_val = price * qty
                    
                    # FİLTRE: En az 10.000$ ve üzeri tekil patlamalar (Balina iştahı)
                    if usd_val > 10000:
                        now = time.time()
                        # Aynı fiyat bölgesini 10 dakika boyunca tekrar bildirme
                        if f"{symbol}_{price}" not in st.session_state.sent or (now - st.session_state.sent[f"{symbol}_{price}"] > 600):
                            
                            # Yön Analizi: Longlar patlıyorsa fiyat aşağı süpürülmüştür (Destek oluşabilir)
                            # Shortlar patlıyorsa fiyat yukarı süpürülmüştür (Direnç oluşabilir)
                            trend = "🔴 LONG LİKİDİTESİ SÜPÜRÜLDÜ" if side == 'SELL' else "🟢 SHORT LİKİDİTESİ SÜPÜRÜLDÜ"
                            action = "🚀 TEPKİ ALIMI GELEBİLİR" if side == 'SELL' else "📉 DÖNÜŞ GELEBİLİR"
                            
                            msg = (f"<b>{trend}</b>\n"
                                   f"━━━━━━━━━━━━━━━\n"
                                   f"💎 <b>#{symbol}</b>\n"
                                   f"💰 <b>Temizlenen Tutar:</b> ${usd_val:,.0f}\n"
                                   f"🎯 <b>Süpürme Fiyatı:</b> {price}\n"
                                   f"💡 <b>Beklenti:</b> {action}\n\n"
                                   f"📊 <a href='https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}PERP'>GRAFİKTE GÖR</a>")
                            
                            send_msg(msg)
                            st.session_state.sent[f"{symbol}_{price}"] = now
                            placeholder.info(f"🚨 Likidite Yakalandı: {symbol} - {usd_val:,.0f}$")

            time.sleep(10) # 10 saniyede bir akışı kontrol et
        except Exception as e:
            time.sleep(5)
