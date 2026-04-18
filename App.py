import streamlit as st

# --- Configurazione Pagina ---
st.set_page_config(page_title="Gestionale Ristorante Pro", layout="wide")
st.title("🍴 Gestionale Ristorante Professionale")

# --- Inizializzazione Dati (Stato della Sessione) ---
# In Streamlit, dobbiamo usare st.session_state per non perdere i dati al ricaricamento
if 'ordini' not in st.session_state:
    st.session_state.ordini = {f"Tavolo {i}": [] for i in range(1, 7)}

menu = {
    "Pasta al Forno": 10.0,
    "Bistecca": 15.0,
    "Insalata": 7.0,
    "Acqua": 2.0,
    "Caffè": 1.5
}

# --- Sidebar per Ordinazioni ---
st.sidebar.header("Prendi Ordine")
tavolo_selezionato = st.sidebar.selectbox("Seleziona Tavolo", list(st.session_state.ordini.keys()))
piatto_selezionato = st.sidebar.selectbox("Seleziona Piatto", list(menu.keys()))

if st.sidebar.button("Aggiungi all'ordine"):
    st.session_state.ordini[tavolo_selezionato].append({
        "piatto": piatto_selezionato,
        "prezzo": menu[piatto_selezionato]
    })
    st.sidebar.success(f"Aggiunto {piatto_selezionato} al {tavolo_selezionato}")

# --- Dashboard Principale ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Stato Tavoli")
    for tavolo, piatti in st.session_state.ordini.items():
        stato = "🔴 Occupato" if piatti else "🟢 Libero"
        st.write(f"**{tavolo}**: {stato} ({len(piatti)} piatti ordinati)")

with col2:
    st.subheader("Conto e Chiusura")
    tavolo_conto = st.selectbox("Seleziona Tavolo per il conto", list(st.session_state.ordini.keys()))
    
    if st.session_state.ordini[tavolo_conto]:
        totale = sum(item['prezzo'] for item in st.session_state.ordini[tavolo_conto])
        st.table(st.session_state.ordini[tavolo_conto])
        st.write(f"### TOTALE: {totale}€")
        
        if st.button("Paga e Libera Tavolo"):
            st.session_state.ordini[tavolo_conto] = []
            st.success("Tavolo liberato correttamente!")
            st.rerun() # Ricarica la pagina per aggiornare lo stato
    else:
        st.info("Il tavolo selezionato è vuoto.")
