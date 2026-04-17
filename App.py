import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3459/3459528.png"

# --- FOTO DI DOMENICO ---
# Se non hai il link diretto, usiamo questa icona professionale "Uomo d'affari"
# Appena hai il tuo link che finisce in .jpg, sostituiscilo qui sotto
FOTO_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png" 

# Impostazioni della pagina
st.set_page_config(page_title="Domenico Work - Consulenza", page_icon="🛡️")

# --- GESTIONE CONTATORE (Parte da 20) ---
# Usiamo st.session_state così il numero aumenta durante la navigazione
if 'contatore' not in st.session_state:
    st.session_state.contatore = 20

# --- STILE CSS PER UN LOOK PROFESSIONALE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8f9fa; }}
    .stButton>button {{
        width: 100%;
        border-radius: 20px;
        background-color: #004a99;
        color: white;
        font-weight: bold;
        border: none;
        height: 3.5em;
    }}
    .counter-box {{
        background-color: white;
        padding: 10px;
        border-radius: 12px;
        border: 2px solid #f7941d;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .counter-number {{
        font-size: 24px;
        font-weight: bold;
        color: #f7941d;
    }}
    .img-circle {{
        border-radius: 50%;
        border: 2px solid #004a99;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER: Foto | Logo | Contatore ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.image(FOTO_URL, width=90)
    st.markdown("<p style='text-align:center; font-weight:bold; margin-top:-10px;'>Domenico</p>", unsafe_allow_html=True)

with col2:
    st.image(LOGO_URL, width=70)
    st.markdown("<p style='text-align:center; font-size:10px; font-weight:bold; color:#004a99;'>DOMENICO WORK</p>", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='counter-box'>
            <div style='font-size: 10px; color: #666;'>CLIENTI SERVITI</div>
            <div class='counter-number'>{st.session_state.contatore}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h2 style='text-align:center; color:#004a99;'>Prenota il tuo Appuntamento</h2>", unsafe_allow_html=True)

# --- FORM DI REGISTRAZIONE ---
with st.form("modulo_prenotazione", clear_on_submit=True):
    nome = st.text_input("Nome e Cognome*")
    email = st.text_input("Tua Email*")
    tel = st.text_input("Telefono/WhatsApp")
    servizio = st.selectbox("Servizio richiesto", ["Polizza Auto", "Casa e Famiglia", "Vita e Risparmio", "Infortuni", "Altro"])
    data_app = st.date_input("Quando preferisci essere contattato?", min_value=datetime.today())
    note = st.text_area("Eventuali note")
    
    invio = st.form_submit_button("CONFERMA REGISTRAZIONE")

if invio:
    if nome and email:
        # Aumentiamo il numero!
        st.session_state.contatore += 1
        st.success(f"Grazie {nome}! Richiesta presa in carico. Sei il cliente n. {st.session_state.contatore}!")
        st.balloons()
        
        # Invio Email tramite FormSubmit
        html_email = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="hidden_form">
                <input type="hidden" name="NUMERO_ORDINE" value="{st.session_state.contatore}">
                <input type="hidden" name="NOME" value="{nome}">
                <input type="hidden" name="EMAIL" value="{email}">
                <input type="hidden" name="TELEFONO" value="{tel}">
                <input type="hidden" name="SERVIZIO" value="{servizio}">
                <input type="hidden" name="DATA" value="{data_app}">
                <input type="hidden" name="_captcha" value="false">
                <input type="hidden" name="_subject" value="DOMENICO WORK: Cliente #{st.session_state.contatore}">
            </form>
            <script>document.getElementById('hidden_form').submit();</script>
        """
        st.components.v1.html(html_email, height=0)
    else:
        st.error("Per favore, compila i campi Nome ed Email.")

st.markdown("---")
st.caption("© 2026 Domenico Work - Consulenza Assicurativa")
