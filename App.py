import streamlit as st
from datetime import datetime

# Configurazione della tua email per le notifiche
TUA_EMAIL = "domenicointer86@gmail.com" 

# Impostazioni estetiche della pagina
st.set_page_config(page_title="Prenota Consulenza Assicurativa", page_icon="🛡️")

# CSS per migliorare l'aspetto da cellulare
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #004a99;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Agenzia Domenico")
st.subheader("Prenota la tua consulenza in pochi clic")

st.write("Compila i dati sottostanti e riceverai una conferma via email.")

# Creazione del modulo di prenotazione
with st.form("modulo_prenotazione", clear_on_submit=True):
    nome = st.text_input("Nome e Cognome*")
    email_cliente = st.text_input("Tua Email*")
    telefono = st.text_input("Numero di Telefono")
    
    motivo = st.selectbox(
        "Motivo della prenotazione", 
        ["Nuova Polizza Auto", "Polizza Casa", "Vita e Previdenza", "Gestione Sinistro", "Rinnovo", "Altro"]
    )
    
    data = st.date_input("Scegli la data", min_value=datetime.today())
    messaggio = st.text_area("Note aggiuntive per Domenico")
    
    submit = st.form_submit_button("CONFERMA PRENOTAZIONE")

if submit:
    if nome and email_cliente:
        # Mostra messaggio di successo immediato al cliente
        st.success(f"Grazie {nome}! La tua richiesta è stata inviata a Domenico.")
        st.balloons()
        
        # Sistema di invio email automatico tramite FormSubmit
        # La prima volta che lo usi, controlla la tua email domenicointer86@gmail.com e conferma il servizio.
        html_code = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="email_form">
                <input type="hidden" name="CLIENTE" value="{nome}">
                <input type="hidden" name="EMAIL_CONTATTO" value="{email_cliente}">
                <input type="hidden" name="TELEFONO" value="{telefono}">
                <input type="hidden" name="MOTIVO" value="{motivo}">
                <input type="hidden" name="DATA_RICHIESTA" value="{data}">
                <input type="hidden" name="NOTE" value="{messaggio}">
                <input type="hidden" name="_subject" value="Nuovo Appuntamento: {nome}">
                <input type="hidden" name="_template" value="table">
                <input type="hidden" name="_captcha" value="false">
            </form>
            <script>
                document.getElementById('email_form').submit();
            </script>
        """
        st.components.v1.html(html_code, height=0)
    else:
        st.error("Per favore, inserisci almeno Nome ed Email.")

st.info("Nota: Se è la prima volta che usi l'app, controlla la cartella Spam dopo l'invio e conferma l'attivazione del servizio.")
