import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3459/3459528.png"
# Link corretto per la tua foto
FOTO_URL = "https://i.ibb.co/x8D75fP0/Domenico.jpg"

st.set_page_config(page_title="Domenico Work", page_icon="🛡️")

if 'contatore' not in st.session_state:
    st.session_state.contatore = 20

# --- STILE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #004a99; color: white; font-weight: bold; }
    .counter-box { background-color: white; padding: 10px; border-radius: 12px; border: 2px solid #f7941d; text-align: center; }
    .counter-number { font-size: 24px; font-weight: bold; color: #f7941d; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.image(FOTO_URL, width=100)
    st.write("**Domenico**")
with col2:
    st.image(LOGO_URL, width=70)
with col3:
    st.markdown(f"<div class='counter-box'><div style='font-size:10px;'>CLIENTI</div><div class='counter-number'>{st.session_state.contatore}</div></div>", unsafe_allow_html=True)

st.markdown("---")

# --- FORM ---
with st.form("my_form"):
    nome = st.text_input("Nome e Cognome*")
    email = st.text_input("Email*")
    tel = st.text_input("Telefono")
    servizio = st.selectbox("Servizio", ["Auto", "Casa", "Vita", "Altro"])
    submit = st.form_submit_button("CONFERMA")

if submit:
    if nome and email:
        st.session_state.contatore += 1
        st.balloons()
        st.success(f"Inviato! Sei il cliente n. {st.session_state.contatore}")
        
        # Sistema di invio mail semplificato
        form_html = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="email_f">
                <input type="hidden" name="Nome" value="{nome}">
                <input type="hidden" name="Email" value="{email}">
                <input type="hidden" name="Servizio" value="{servizio}">
                <input type="hidden" name="_captcha" value="false">
            </form>
            <script>document.getElementById('email_f').submit();</script>
        """
        st.components.v1.html(form_html, height=0)
    else:
        st.error("Mancano Nome o Email!")
