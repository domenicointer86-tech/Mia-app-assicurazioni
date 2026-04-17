import streamlit as st
from datetime import datetime

# Sostituisci questa email con la tua email professionale
TUA_EMAIL = "tuaemail@esempio.it" 

st.set_page_config(page_title="Prenota Consulenza", page_icon="🛡️")

st.title("🛡️ Prenota la tua Consulenza")
st.write("Compila il modulo per fissare un appuntamento. Riceverai una conferma via email.")

# Creazione del modulo
with st.form("modulo_prenotazione"):
    nome = st.text_input("Nome e Cognome*")
    email_cliente = st.text_input("Tua Email*")
    motivo = st.selectbox("Motivo della consulenza", ["Nuova Polizza", "Rinnovo", "Sinistro", "Consulenza Generica"])
    data = st.date_input("Data preferita", min_value=datetime.today())
    messaggio = st.text_area("Note o dettagli aggiuntivi")
    
    # Questo tasto invia i dati
    submit = st.form_submit_button("Conferma e Invia Richiesta")

if submit:
    if nome and email_cliente:
        # Messaggio di successo per il cliente
        st.success(f"Grazie {nome}! La tua richiesta è stata presa in carico.")
        st.balloons()
        
        # Link invisibile per inviare la notifica a te
        # Al primo invio, dovrai cliccare su un link nella mail per attivare il servizio (è gratis)
        st.markdown(f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="email_form">
                <input type="hidden" name="Nome" value="{nome}">
                <input type="hidden" name="Email_Cliente" value="{email_cliente}">
                <input type="hidden" name="Motivo" value="{motivo}">
                <input type="hidden" name="Data" value="{data}">
                <input type="hidden" name="Messaggio" value="{messaggio}">
                <input type="hidden" name="_next" value="https://tuo-sito.streamlit.app">
                <input type="hidden" name="_subject" value="NUOVA PRENOTAZIONE: {nome}">
            </form>
            <script>
                document.getElementById('email_form').submit();
            </script>
        """, unsafe_allow_html=True)
        
    else:
        st.error("Per favore, inserisci Nome ed Email per procedere.")
