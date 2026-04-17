import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 

# Icona professionale garantita (Scudo Protezione)
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3459/3459528.png"

# Impostazioni della pagina
st.set_page_config(page_title="Domenico Work - Consulenza", page_icon="🛡️")

# --- STILE CSS PERSONALIZZATO ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #f4f7f9;
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 25px;
        height: 3.5em;
        background-color: #004a99; /* Blu professionale */
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    h1, h3 {{
        text-align: center;
        color: #004a99;
    }}
    .logo-text {{
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #004a99;
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- VISUALIZZAZIONE LOGO ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image(LOGO_URL, width=120)

st.markdown("<div class='logo-text'>DOMENICO WORK</div>", unsafe_allow_html=True)
st.markdown("<h3>Prenota la tua Consulenza</h3>", unsafe_allow_html=True)
st.write("Compila il modulo qui sotto e verrai ricontattato da Domenico.")

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
        st.success(f"Grazie {nome}! Richiesta inviata con successo.")
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
        st.error("Inserisci nome ed email per procedere.")

st.markdown("---")
st.caption("© 2024 Domenico Work - Consulenza Assicurativa Professionale")
