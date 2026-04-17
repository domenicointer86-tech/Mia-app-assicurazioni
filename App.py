import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3459/3459528.png"

# --- LA TUA FOTO DA IMGBB ---
FOTO_URL = "https://i.ibb.co/x8D75fP0/your-image.jpg" # Link diretto ottimizzato

# Impostazioni della pagina
st.set_page_config(page_title="Domenico Work - Consulenza", page_icon="🛡️")

# --- GESTIONE CONTATORE ---
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
        border: none;
    }}
    .counter-box {{
        background-color: white;
        padding: 10px;
        border-radius: 12px;
        border: 2px solid #f7941d;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .counter-number {{
        font-size: 24px;
        font-weight: bold;
        color: #f7941d;
    }}
    .profile-pic {{
        border-radius: 50%;
        border: 3px solid #004a99;
        object-fit: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER: Foto | Logo | Contatore ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    # Mostriamo la tua foto vera
    st.image(FOTO_URL, width=100)
    st.markdown("<p style='text-align:center; font-weight:bold; color:#004a99; margin-top:-5px;'>Domenico</p>", unsafe_allow_html=True)

with col2:
    st.image(LOGO_URL, width=75)
    st.markdown("<p style='text-align:center; font-size:10px; font-weight:bold; color:#004a99;'>DOMENICO WORK</p>", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='counter-box'>
            <div style='font-size: 10px; color: #666; font-weight:bold;'>CLIENTI SERVITI</div>
            <div class='counter-number'>{st.session_state.numero_clienti}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h2 style='text-align:center; color:#004a99;'>Prenota il tuo Appuntamento</h2>", unsafe_allow_html=True)

# --- FORM DI REGISTRAZIONE ---
with st.form("modulo_prenotazione"):
    nome = st.text_input("Nome e Cognome*")
    email = st.text_input("Tua Email*")
    tel = st.text_input("Telefono / WhatsApp")
    servizio = st.selectbox("Di cosa hai bisogno?", ["Polizza Auto", "Casa e Famiglia", "Vita e Risparmio", "Infortuni", "Altro"])
    data_app = st.date_input("Giorno preferito", min_value=datetime.today())
    
    invio = st.form_submit_button("CONFERMA REGISTRAZIONE")

if invio:
    if nome and email:
        # Aumentiamo il numero
        st.session_state.numero_clienti += 1
        st.success(f"Grazie {nome}! Richiesta inviata. Sei il cliente n. {st.session_state.numero_clienti}!")
        st.balloons()
        
        # Invio Email tramite FormSubmit
        html_email = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="hidden_form">
                <input type="hidden" name="N_CLIENTE" value="{st.session_state.numero_clienti}">
                <input type="hidden" name="NOME" value="{nome}">
                <input type="hidden" name="EMAIL" value="{email}">
                <input type="hidden" name="TELEFONO" value="{tel}">
                <input type="hidden" name="SERVIZIO" value="{servizio}">
                <input type="hidden" name="_captcha" value="false">
                <input type="hidden" name="_subject" value="DOMENICO WORK: Nuova Prenotazione #{st.session_state.numero_clienti}">
            </form>
            <script>document.getElementById('hidden_form').submit();</script>
        """
        st.components.v1.html(html_email, height=0)
        
        # Ricarica per aggiornare il contatore visibile
        st.rerun()
    else:
        st.error("Inserisci Nome ed Email per continuare.")

st.markdown("---")
st.caption("© 2026 Domenico Work - Consulenza Assicurativa Professionale")
