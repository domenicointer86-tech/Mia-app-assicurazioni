import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3459/3459528.png"
FOTO_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png" 

# Impostazioni della pagina
st.set_page_config(page_title="Domenico Work - Consulenza", page_icon="🛡️")

# --- FIX CONTATORE ---
# Inizializziamo il contatore solo se non esiste già
if 'numero_clienti' not in st.session_state:
    st.session_state.numero_clienti = 20

# --- STILE CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8f9fa; }}
    .stButton>button {{
        width: 100%;
        border-radius: 20px;
        background-color: #004a99;
        color: white;
        font-weight: bold;
        height: 3.5em;
    }}
    .counter-box {{
        background-color: white;
        padding: 10px;
        border-radius: 12px;
        border: 2px solid #f7941d;
        text-align: center;
    }}
    .counter-number {{
        font-size: 24px;
        font-weight: bold;
        color: #f7941d;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.image(FOTO_URL, width=90)
    st.markdown("<p style='text-align:center; font-weight:bold;'>Domenico</p>", unsafe_allow_html=True)

with col2:
    st.image(LOGO_URL, width=70)
    st.markdown("<p style='text-align:center; font-size:10px; font-weight:bold; color:#004a99;'>DOMENICO WORK</p>", unsafe_allow_html=True)

with col3:
    # Mostriamo il numero aggiornato
    st.markdown(f"""
        <div class='counter-box'>
            <div style='font-size: 10px; color: #666;'>CLIENTI SERVITI</div>
            <div class='counter-number'>{st.session_state.numero_clienti}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h2 style='text-align:center; color:#004a99;'>Prenota il tuo Appuntamento</h2>", unsafe_allow_html=True)

# --- FORM ---
# Usiamo un trucco: non resettiamo il form subito per permettere al contatore di vedersi
with st.form("modulo_prenotazione"):
    nome = st.text_input("Nome e Cognome*")
    email = st.text_input("Tua Email*")
    tel = st.text_input("Telefono")
    servizio = st.selectbox("Servizio", ["Auto", "Casa", "Vita", "Infortuni", "Altro"])
    data_app = st.date_input("Data", min_value=datetime.today())
    
    invio = st.form_submit_button("CONFERMA REGISTRAZIONE")

if invio:
    if nome and email:
        # AUMENTIAMO IL NUMERO E LO SALVIAMO NELLA SESSIONE
        st.session_state.numero_clienti += 1
        
        st.success(f"Grazie {nome}! Richiesta inviata. Sei il cliente n. {st.session_state.numero_clienti}!")
        st.balloons()
        
        # Invio Email
        html_email = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="hidden_form">
                <input type="hidden" name="CLIENTE_NUMERO" value="{st.session_state.numero_clienti}">
                <input type="hidden" name="NOME" value="{nome}">
                <input type="hidden" name="EMAIL" value="{email}">
                <input type="hidden" name="_captcha" value="false">
                <input type="hidden" name="_subject" value="DOMENICO WORK: Nuova Prenotazione #{st.session_state.numero_clienti}">
            </form>
            <script>document.getElementById('hidden_form').submit();</script>
        """
        st.components.v1.html(html_email, height=0)
        
        # Forziamo il ricaricamento della pagina per mostrare il nuovo numero nel box in alto
        st.rerun()
    else:
        st.error("Inserisci Nome ed Email!")

st.markdown("---")
st.caption("© 2026 Domenico Work")
