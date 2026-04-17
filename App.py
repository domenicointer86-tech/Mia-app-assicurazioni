import streamlit as st
from datetime import datetime
import os

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3459/3459528.png"
FOTO_DOMENICO = "domenico.jpg" # Carica la tua foto su GitHub con questo nome

# Impostazioni della pagina
st.set_page_config(page_title="Domenico Work - Consulenza", page_icon="🛡️")

# Inizializzazione contatore (Nota: si resetta se l'app si spegne, a meno di usare un DB)
if 'contatore' not in st.session_state:
    st.session_state.contatore = 157 # Partiamo da un numero base di clienti soddisfatti

# --- STILE CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4f7f9; }}
    .stButton>button {{
        width: 100%;
        border-radius: 25px;
        background-color: #004a99;
        color: white;
        font-weight: bold;
    }}
    .counter-box {{
        background-color: #ffffff;
        padding: 10px;
        border-radius: 15px;
        border: 2px solid #f7941d;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .counter-number {{
        font-size: 22px;
        font-weight: bold;
        color: #f7941d;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- INTESTAZIONE CON FOTO E CONTATORE ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    # Se carichi la foto 'domenico.jpg' su GitHub apparirà qui
    if os.path.exists(FOTO_DOMENICO):
        st.image(FOTO_DOMENICO, width=100)
    else:
        st.write("👤 [Carica foto]")

with col2:
    st.image(LOGO_URL, width=80)
    st.markdown("<div style='text-align:center; font-weight:bold; color:#004a99;'>DOMENICO WORK</div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='counter-box'>
            <div style='font-size: 10px; color: #666;'>CLIENTI SERVITI</div>
            <div class='counter-number'>{st.session_state.contatore}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h3 style='text-align:center;'>Prenota il tuo Appuntamento</h3>", unsafe_allow_html=True)

# --- FORM ---
with st.form("modulo_domenico", clear_on_submit=True):
    nome = st.text_input("Nome e Cognome*")
    email_cliente = st.text_input("Tua Email*")
    telefono = st.text_input("Telefono")
    motivo = st.selectbox("Servizio", ["Auto", "Casa", "Vita", "Sinistro", "Rinnovo", "Altro"])
    data = st.date_input("Giorno", min_value=datetime.today())
    messaggio = st.text_area("Note")
    submit = st.form_submit_button("INVIA RICHIESTA")

if submit:
    if nome and email_cliente:
        # Aumenta il contatore per la sessione attuale
        st.session_state.contatore += 1
        st.success(f"Grazie {nome}! Sei il cliente n. {st.session_state.contatore}. Richiesta inviata!")
        st.balloons()
        
        # Invio Email (FormSubmit)
        html_code = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="email_form">
                <input type="hidden" name="Cliente" value="{nome}">
                <input type="hidden" name="Email" value="{email_cliente}">
                <input type="hidden" name="Servizio" value="{motivo}">
                <input type="hidden" name="Data" value="{data}">
                <input type="hidden" name="_captcha" value="false">
                <input type="hidden" name="_subject" value="DOMENICO WORK: Cliente n. {st.session_state.contatore}">
            </form>
            <script>document.getElementById('email_form').submit();</script>
        """
        st.components.v1.html(html_code, height=0)
    else:
        st.error("Inserisci nome ed email.")

st.caption("© 2024 Domenico Work - Consulenza Professionale")
