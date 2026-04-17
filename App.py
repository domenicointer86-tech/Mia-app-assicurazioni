import streamlit as st
from datetime import datetime
import os

# --- IMPOSTAZIONI DEL LOGO "DOMENICO WORK" ---
# Se hai salvato il logo generato come 'logo.png' nella stessa cartella di app.py
LOGO_PATH = "logo.png" 

# Configurazione della tua email per le notifiche (domenicointer86@gmail.com)
TUA_EMAIL = "domenicointer86@gmail.com" 

# Impostazioni estetiche della pagina (abbinate ai colori del logo: Teal, Arancio, Verde)
st.set_page_config(page_title="Domenico Work - Consulenza Assicurativa", page_icon="🛡️")

# CSS per personalizzare l'aspetto e i colori (usando i colori teal e arancio)
st.markdown(f"""
    <style>
    .main {{ background-color: #f0f7f7; }} /* Sfondo leggero teal */
    .stApp {{ border-top: 5px solid #007777; }} /* Bordo superiore teal */
    
    .stButton>button {{
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        background-color: #f7941d; /* Colore arancio del logo per il pulsante */
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .stButton>button:hover {{
        background-color: #cc7a14; /* Arancio più scuro al passaggio del mouse */
    }}
    </style>
    """, unsafe_allow_html=True)

# --- VISUALIZZAZIONE DEL LOGO ---
if os.path.exists(LOGO_PATH):
    # Centriamo l'immagine utilizzando le colonne di Streamlit
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_PATH, use_column_width=True, caption="Domenico Work")
else:
    # Se il file logo.png non è stato caricato, mostriamo un titolo testuale pulito
    st.title("🛡️ DOMENICO work")
    st.subheader("La tua Segreteria Virtuale per la Consulenza")

st.markdown("---")
st.write("Compila i dati sottostanti e Domenico riceverà subito la tua richiesta.")

# --- FORM DI PRENOTAZIONE (Migliorato) ---
with st.form("modulo_prenotazione", clear_on_submit=True):
    nome = st.text_input("Nome e Cognome*", placeholder="Es. Domenico Rossi")
    email_cliente = st.text_input("Tua Email*", placeholder="Es. email@esempio.it")
    telefono = st.text_input("Numero di Telefono (Facoltativo)")
    
    motivo = st.selectbox(
        "Motivo della prenotazione", 
        ["Nuova Polizza Auto", "Polizza Casa", "Vita/Previdenza", "Gestione Sinistro", "Rinnovo Contratto", "Altro"]
    )
    
    data = st.date_input("Scegli la data dell'appuntamento", min_value=datetime.today())
    messaggio = st.text_area("Note aggiuntive per Domenico (Facoltativo)")
    
    submit = st.form_submit_button("RICHIEDI APPUNTAMENTO")

# --- LOGICA DI INVIO ---
if submit:
    if nome and email_cliente:
        # Messaggio di successo al cliente
        st.success(f"Grazie {nome}! La tua richiesta è stata inviata. Domenico ti contatterà presto.")
        st.balloons()
        
        # Sistema di invio email (FormSubmit) - Già attivato
        html_code = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="email_form">
                <input type="hidden" name="CLIENTE" value="{nome}">
                <input type="hidden" name="EMAIL_CONTATTO" value="{email_cliente}">
                <input type="hidden" name="TELEFONO" value="{telefono}">
                <input type="hidden" name="MOTIVO" value="{motivo}">
                <input type="hidden" name="DATA_RICHIESTA" value="{data}">
                <input type="hidden" name="NOTE" value="{messaggio}">
                <input type="hidden" name="_subject" value="DOMENICO WORK - Nuovo Appuntamento: {nome}">
                <input type="hidden" name="_template" value="table">
                <input type="hidden" name="_captcha" value="false">
                <input type="hidden" name="_next" value="https://domenicowork.streamlit.app">
            </form>
            <script>
                document.getElementById('email_form').submit();
            </script>
        """
        st.components.v1.html(html_code, height=0)
    else:
        st.error("Per favore, inserisci Nome ed Email per procedere.")

st.info("Hai un'urgenza? Chiamami subito o inviami un messaggio su WhatsApp.")
