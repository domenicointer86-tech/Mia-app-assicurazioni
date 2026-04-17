import streamlit as st
from datetime import datetime

st.title("🛡️ Prenota Consulenza")
st.write("Benvenuto! Compila i campi per fissare un appuntamento.")

# Campi semplici
nome = st.text_input("Nome e Cognome")
email = st.text_input("Tua Email")
motivo = st.selectbox("Motivo", ["Auto", "Casa", "Vita", "Sinistro", "Altro"])
data = st.date_input("Data", min_value=datetime.today())
nota = st.text_area("Note aggiuntive")

if st.button("Conferma Prenotazione"):
    if nome and email:
        st.success(f"Grazie {nome}! Richiesta inviata per il {data}.")
        st.balloons()
    else:
        st.error("Inserisci nome ed email!")
