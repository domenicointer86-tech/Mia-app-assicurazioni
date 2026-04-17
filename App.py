import streamlit as st

# Configurazione iniziale
st.set_page_config(page_title="Domenico Bar", layout="wide")

# Inizializzazione dati
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 11)}

st.title("🍹 Domenico Risto-Management")

# Controlliamo i tavoli
t_sel = st.selectbox("Seleziona Tavolo", list(st.session_state.tavoli.keys()))

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Menu Rapido")
    if st.button("☕ Aggiungi Caffè (1.20€)"):
        st.session_state.tavoli[t_sel].append({"n": "Caffè", "p": 1.20})
        st.rerun()
    if st.button("🍺 Aggiungi Birra (5.00€)"):
        st.session_state.tavoli[t_sel].append({"n": "Birra", "p": 5.00})
        st.rerun()

with col2:
    st.subheader(f"Conto {t_sel}")
    ordine = st.session_state.tavoli[t_sel]
    totale = sum(item['p'] for item in ordine)
    for item in ordine:
        st.write(f"- {item['n']} €{item['p']:.2f}")
    st.divider()
    st.header(f"TOTALE: €{totale:.2f}")
    if st.button("Pulisci Tavolo"):
        st.session_state.tavoli[t_sel] = []
        st.rerun()
