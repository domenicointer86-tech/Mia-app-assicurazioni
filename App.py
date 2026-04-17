import streamlit as st
from datetime import datetime
import os

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
LOGO_PATH = "logo.png" 

# Impostazioni della pagina
st.set_page_config(page_title="Domenico Work - Consulenza", page_icon="🛡️")

# --- STILE CSS PERSONALIZZATO ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #f0f7f7;
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 25px;
        height: 3.5em;
        background-color: #f7941d; /* Arancio Domenico Work */
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(247, 148, 29, 0.3);
    }}
    .stTextInput>div>div>input, .stSelectbox>div>div>select {{
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- VISUALIZZAZIONE LOGO ---
if os.path.exists(LOGO_PATH):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_PATH, use_column_width=True)
else:
    st.title("🛡️ DOMENICO work")

st.markdown("<h3 style='text-align: center; color: #007777;'>Prenota la tua Consulenza</h3>", unsafe_allow_html=True)
st.write("Compila il modulo qui sotto. Domenico riceverà la tua richiesta all'istante.")

# --- FORM DI PRENOTAZIONE ---
with st.form("modulo_domenico", clear_on_submit=True):
    nome = st.text_input("Nome e Cognome*")
    email_cliente = st.text_input("Tua Email*")
    telefono = st.text_input("Telefono")
    
    motivo = st.selectbox(
        "Di cosa hai bisogno?", 
        ["Nuova Polizza Auto", "Polizza Casa", "Vita e Risparmio", "Gestione Sinistro", "Rinnovo", "Altro"]
    )
    
    data = st.date_input("Scegli il giorno", min_value=datetime.today())
    messaggio = st.text_area("Note per Domenico")
    
    submit = st.form_submit_button("INVIA RICHIESTA")

# --- LOGICA DI INVIO ---
if submit:
    if nome and email_cliente:
        st.success(f"Ottimo {nome}! Richiesta inviata. Domenico ti ricontatterà a breve.")
        st.balloons()
        
        # Invio Email tramite FormSubmit
        html_code = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="email_form">
                <input type="hidden" name="Cliente" value="{nome}">
                <input type="hidden" name="Email" value="{email_cliente}">
                <input type="hidden" name="Tel" value="{telefono}">
                <input type="hidden" name="Servizio" value="{motivo}">
                <input type="hidden" name="Data" value="{data}">
                <input type="hidden" name="Note" value="{messaggio}">
                <input type="hidden" name="_captcha" value="false">
                <input type="hidden" name="_subject" value="DOMENICO WORK: Nuova richiesta da {nome}">
                <input type="hidden" name="_template" value="table">
            </form>
            <script>document.getElementById('email_form').submit();</script>
        """
        st.components.v1.html(html_code, height=0)
    else:
        st.error("Ops! Inserisci nome ed email per poter essere ricontattato.")

st.markdown("---")
st.caption("© 2026 Domenico Work - Consulenza Assicurativa Professionale")
