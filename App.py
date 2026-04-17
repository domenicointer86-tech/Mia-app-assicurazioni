import streamlit as st

# --- 1. INIZIALIZZAZIONE (Questo salva i tuoi dati in memoria) ---
if 'menu_personale' not in st.session_state:
    st.session_state.menu_personale = {
        "Caffetteria": {"Caffè": 1.20},
        "Bevande": {"Birra": 4.00},
        "Cucina": {"Panino": 6.00}
    }

if 'ordini' not in st.session_state:
    st.session_state.ordini = {f"Tavolo {i}": [] for i in range(1, 13)}

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Domenico Smart Bar", layout="wide")

# --- 3. TENDINA LATERALE (SIDEBAR) PER AGGIUNGERE ---
with st.sidebar:
    st.header("➕ AGGIUNGI AL MENU")
    st.write("Usa questo modulo per inserire i tuoi prodotti:")
    
    # Scelta categoria
    cat = st.selectbox("Categoria", ["Caffetteria", "Bevande", "Cucina"])
    
    # Inserimento nome e prezzo
    nuovo_nome = st.text_input("Nome Prodotto (es. Pasta)")
    nuovo_prezzo = st.number_input("Prezzo (€)", min_value=0.0, step=0.50, format="%.2f")
    
    if st.button("SALVA NEL MENU"):
        if nuovo_nome:
            # Salviamo nel dizionario in memoria
            st.session_state.menu_personale[cat][nuovo_nome] = nuovo_prezzo
            st.success(f"✅ {nuovo_nome} aggiunto!")
            st.rerun() # Forza l'app a ricaricarsi e mostrare il nuovo tasto
        else:
            st.error("Scrivi il nome del prodotto!")

    st.markdown("---")
    st.write("**Menu Attuale:**")
    st.json(st.session_state.menu_personale) # Ti mostra la lista per controllo

# --- 4. SCHERMATA PRINCIPALE (CASSA) ---
st.title("🍹 Cassa Domenico")

tavolo_attivo = st.selectbox("Seleziona Tavolo", list(st.session_state.ordini.keys()))

col_tasti, col_conto = st.columns([2, 1])

with col_tasti:
    st.subheader("🛒 Seleziona Prodotti")
    # Creiamo i tasti per ogni categoria
    for categoria, prodotti in st.session_state.menu_personale.items():
        st.write(f"**{categoria}**")
        cols = st.columns(3)
        for i, (nome, prezzo) in enumerate(prodotti.items()):
            if cols[i % 3].button(f"{nome}\n€{prezzo:.2f}", key=f"btn_{tavolo_attivo}_{nome}"):
                st.session_state.ordini[tavolo_attivo].append({"n": nome, "p": prezzo})
                st.rerun()

with col_conto:
    st.subheader(f"🧾 Conto {tavolo_attivo}")
    lista = st.session_state.ordini[tavolo_attivo]
    totale = 0.0
    
    if not lista:
        st.info("Tavolo vuoto")
    else:
        for item in lista:
            st.write(f"• {item['n']} - €{item['p']:.2f}")
            totale += item['p']
        
        st.divider()
        st.markdown(f"### TOTALE: €{totale:.2f}")
        
        if st.button("CHIUDI E PULISCI TAVOLO", type="primary"):
            st.session_state.ordini[tavolo_attivo] = []
            st.balloons()
            st.rerun()
