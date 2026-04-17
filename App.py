import streamlit as st

# Configurazione base
st.set_page_config(page_title="Domenico Bar", layout="wide")

# Inizializzazione dati
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}
if 'menu' not in st.session_state:
    st.session_state.menu = {"Bar": {"Caffè": 1.2, "Birra": 5.0}, "Cucina": {"Pizza": 8.0}}

# --- SIDEBAR (LA TENDINA) ---
with st.sidebar:
    st.header("⚙️ Gestione")
    opzione = st.radio("Vai a:", ["Cassa", "Aggiungi Prodotto"])
    
    if opzione == "Aggiungi Prodotto":
        st.subheader("Nuovo Articolo")
        cat = st.selectbox("Categoria", list(st.session_state.menu.keys()))
        nome = st.text_input("Nome")
        prezzo = st.number_input("Prezzo €", min_value=0.0)
        if st.button("Salva"):
            st.session_state.menu[cat][nome] = prezzo
            st.success("Aggiunto!")

# --- SCHERMATA CASSA ---
if opzione == "Cassa":
    st.title("🍹 Domenico Risto-Management")
    
    t_sel = st.selectbox("Seleziona Tavolo", list(st.session_state.tavoli.keys()))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🛒 Menu")
        for cat, prods in st.session_state.menu.items():
            st.write(f"**{cat}**")
            cols = st.columns(3)
            for i, (n, p) in enumerate(prods.items()):
                if cols[i%3].button(f"{n}\n€{p}", key=f"{t_sel}_{n}"):
                    st.session_state.tavoli[t_sel].append({"n": n, "p": p})
                    st.rerun()

    with col2:
        st.subheader(f"🧾 Conto {t_sel}")
        conto = st.session_state.tavoli[t_sel]
        tot = sum(item['p'] for item in conto)
        for item in conto:
            st.write(f"- {item['n']} €{item['p']:.2f}")
        st.divider()
        st.header(f"TOT: €{tot:.2f}")
        if st.button("PULISCI TAVOLO"):
            st.session_state.tavoli[t_sel] = []
            st.rerun()
