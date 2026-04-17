import streamlit as st
from datetime import datetime, time

# Configurazione Pagina
st.set_page_config(page_title="Agenzia Assicurazioni - Prenota", page_icon="🛡️")

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #004a99; color: white; }
    </style>
    """, unsafe_allow_html=True)

## --- LOGICA DELL'APP ---

st.title("🛡️ Prenota la tua Consulenza")
st.subheader("Gestione rapida e professionale per le tue polizze")

with st.form("booking_form"):
    st.write("Inserisci i dettagli per fissare un appuntamento")
    
    # 1. Anagrafica
    nome = st.text_input("Nome e Cognome")
    email = st.text_input("Indirizzo Email")
    
    # 2. Motivo della consulenza
    motivo = st.selectbox(
        "Motivo della prenotazione",
        ["Nuova Polizza Auto", "Polizza Casa/Fabbricati", "Previdenza e Vita", "Gestione Sinistro", "Rinnovo Contratto", "Altro"]
    )
    
    descrizione = st.text_area("Breve descrizione dell'esigenza")
    
    # 3. Data e Ora
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Scegli la data", min_value=datetime.today())
    with col2:
        # Definizione slot orari (es. ogni ora dalle 9 alle 18)
        orario = st.time_input("Scegli l'orario", value=time(9, 0))

    # 4. Modalità
    tipo_incontro = st.radio("Modalità di incontro", ["In Agenzia", "Videochiamata", "Telefonica"])

    # Bottone di invio
    submit = st.form_submit_button("CONFERMA PRENOTAZIONE")

if submit:
    if nome and email:
        # Qui l'app elabora i dati
        st.success(f"Grazie {nome}! La tua richiesta per '{motivo}' il giorno {data} alle ore {orario} è stata inviata.")
        st.info("Riceverai una mail di conferma con il link o l'indirizzo dell'ufficio.")
        
        # NOTA TECNICA: Qui si inserirebbe il codice per inviare la mail a te e al cliente
        # e per salvare i dati su un database (es. Google Sheets o SQLite)
    else:
        st.error("Per favore, compila tutti i campi obbligatori.")

---
### Area Gestione (Solo per te)
if st.checkbox("Accedi come Consulente"):
    password = st.text_input("Password", type="password")
    if password == "admin123": # Password di esempio
        st.write("### 📅 Appuntamenti Ricevuti")
        # Qui verrebbe visualizzata la tabella con tutte le prenotazioni
        st.write("Nessuna nuova prenotazione presente.")
