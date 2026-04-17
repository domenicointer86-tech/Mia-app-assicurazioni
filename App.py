import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 

# --- INIZIALIZZAZIONE MENU (Session State per renderlo modificabile) ---
if 'menu_dinamico' not in st.session_state:
    st.session_state.menu_dinamico = {
        "Caffetteria": {"Caffè": 1.20, "Cappuccino": 1.50},
        "Bevande": {"Birra": 4.00, "Spritz": 5.00},
        "Cucina": {"Panino": 6.00, "Tagliere": 12.00}
    }

if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}

st.set_page_config(page_title="Domenico Pro", layout="wide")

# --- BARRA LATERALE (LA TENDINA CHE VOLEVI) ---
with st.sidebar:
    st.header("⚙️ Gestione Menu")
    st.write("Aggiungi un nuovo prodotto alla lista:")
    
    cat_nuova = st.selectbox("In quale categoria?", list(st.session_state.menu_dinamico.keys()))
    nome_nuovo = st.text_input("Nome (es. Coca Cola)")
    prezzo_nuovo = st.number_input("Prezzo (€)", min_value=0.0, step=0.10)
    
    if st.button("➕ AGGIUNGI AL MENU"):
        if nome_nuovo:
            st.session_state.menu_dinamico[cat_nuova][nome_nuovo] = prezzo_nuovo
            st.success(f"Aggiunto: {nome_nuovo}")
            st.rerun() # Ricarica l'app per mostrare il nuovo tasto
    
    st.markdown("---")
    st.info("I prodotti aggiunti appariranno subito nel quadrante degli ordini.")

# --- SCHERMATA PRINCIPALE ---
st.title("🍹 Domenico Smart Bar")

# Monitor Tavoli
st.subheader("📊 Stato Tavoli")
st_cols = st.columns(6)
for i, (t_nome, t_lista) in enumerate(st.session_state.tavoli.items()):
    colore = "🔴" if t_lista else "🟢"
    st_cols[i % 6].markdown(f"**{t_nome}** {colore}")

st.markdown("---")

# Selezione Tavolo e Ordini
col_sx, col_dx = st.columns([2, 1])

with col_sx:
    tavolo_sel = st.selectbox("📍 Gestisci:", list(st.session_state.tavoli.keys()))
    
    # Selettore categoria per i tasti
    cat_visualizzata = st.radio("Reparto:", list(st.session_state.menu_dinamico.keys()), horizontal=True)
    
    st.write(f"**Tocca per aggiungere a {tavolo_sel}:**")
    tasti_cols = st.columns(3)
    prodotti = st.session_state.menu_dinamico[cat_visualizzata]
    
    for i, (nome, prezzo) in enumerate(prodotti.items()):
        if tasti_cols[i % 3].button(f"{nome}\n€{prezzo:.2f}", key=f"{nome}_{i}", use_container_width=True):
            st.session_state.tavoli[tavolo_sel].append({"n": nome, "p": prezzo})
            st.rerun()

with col_dx:
    st.subheader(f"🧾 Conto {tavolo_sel}")
    lista_ordini = st.session_state.tavoli[tavolo_sel]
    totale = 0.0
    
    if not lista_ordini:
        st.write("Nessun ordine")
    else:
        for item in lista_ordini:
            st.write(f"{item['n']} - €{item['p']:.2f}")
            totale += item['p']
        st.markdown(f"### TOTALE: €{totale:.2f}")
        
        c1, c2 = st.columns(2)
        if c1.button("🗑️ Svuota"):
            st.session_state.tavoli[tavolo_sel] = []
            st.rerun()
        if c2.button("💰 Chiudi", type="primary"):
            st.balloons()
            # Logica invio mail qui...
            st.session_state.tavoli[tavolo_sel] = []
            st.rerun()
