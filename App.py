import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
TUA_FOTO = "https://i.ibb.co/x8D75fP0/Domenico.jpg"
LOGO_ASSICURAZIONE = "https://cdn-icons-png.flaticon.com/512/3459/3459528.png"
WHATSAPP_LINK = "https://wa.me/39XXXXXXXXXX" # Sostituisci le X con il tuo numero (es: 393331234567)

st.set_page_config(page_title="Domenico Work - Consulenza", page_icon="🛡️", layout="centered")

if 'contatore' not in st.session_state:
    st.session_state.contatore = 20

# --- STILE CSS PREMIUM ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, #ffffff 0%, #f0f4f8 100%);
    }}
    .main-header {{
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 30px;
        background: linear-gradient(90deg, #004a99 0%, #0066cc 100%);
        color: white;
        font-weight: bold;
        height: 3.5em;
        border: none;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
    }}
    .feature-box {{
        padding: 15px;
        background: white;
        border-radius: 15px;
        text-align: center;
        border-bottom: 3px solid #004a99;
    }}
    .counter-text {{
        color: #f7941d;
        font-size: 28px;
        font-weight: bold;
    }}
    .whatsapp-btn {{
        background-color: #25d366;
        color: white;
        padding: 10px 20px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
with st.container():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col1:
        st.image(TUA_FOTO, width=100)
    with col2:
        st.image(LOGO_ASSICURAZIONE, width=80)
        st.markdown("<h3 style='text-align:center; color:#004a99; margin-top:-10px;'>DOMENICO WORK</h3>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div style='text-align:center;'>
                <p style='font-size:10px; margin-bottom:0;'>CLIENTI SODDISFATTI</p>
                <span class='counter-text'>{st.session_state.contatore}</span>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# --- PUNTI DI FORZA ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='feature-box'>🛡️<br><b>Sicurezza</b></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='feature-box'>⚡<br><b>Rapidità</b></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='feature-box'>💰<br><b>Risparmio</b></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- CORPO PRINCIPALE ---
col_form, col_info = st.columns([1.5, 1])

with col_form:
    st.markdown("#### 📝 Richiedi un preventivo")
    with st.form("form_premium", clear_on_submit=True):
        nome = st.text_input("Nome e Cognome")
        email = st.text_input("Email")
        tel = st.text_input("Telefono")
        servizio = st.selectbox("Cosa ti occorre?", ["Polizza Auto", "Protezione Casa", "Assicurazione Vita", "Consulenza Sinistro"])
        note = st.text_area("Note aggiuntive")
        submit = st.form_submit_button("INVIA RICHIESTA ORA")

with col_info:
    st.markdown("#### 📞 Contatto Diretto")
    st.write("Hai urgenza? Scrivimi direttamente su WhatsApp per una risposta immediata.")
    st.markdown(f"<a href='{WHATSAPP_LINK}' class='whatsapp-btn'>💬 WhatsApp</a>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("Disponibile Lun-Ven: 09:00 - 18:30")

# --- LOGICA INVIO ---
if submit:
    if nome and email:
        st.session_state.contatore += 1
        st.balloons()
        st.success(f"Grazie {nome}! Richiesta n. {st.session_state.contatore} inviata con successo.")
        
        # FormSubmit
        form_html = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="f">
                <input type="hidden" name="Cliente" value="{nome}">
                <input type="hidden" name="Servizio" value="{servizio}">
                <input type="hidden" name="Telefono" value="{tel}">
                <input type="hidden" name="_captcha" value="false">
            </form>
            <script>document.getElementById('f').submit();</script>
        """
        st.components.v1.html(form_html, height=0)
    else:
        st.error("Compila i campi obbligatori (Nome ed Email).")

st.markdown("<br><hr><center><p style='color:gray;'>© 2026 Domenico Work - Esperto in Soluzioni Assicurative</p></center>", unsafe_allow_html=True)
