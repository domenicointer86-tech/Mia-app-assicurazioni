import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Domenico Risto-Pro", layout="wide")

# --- DATABASE IN MEMORIA ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Caffetteria": {"Caffè": 1.2, "Cappuccino": 1.5, "Cornetto": 1.2},
        "Bevande": {"Birra": 4.5, "Spritz": 5.0, "Acqua": 1.5},
        "Cucina": {"Panino": 6.5, "Tagliere": 12.0, "Primo": 10.0}
    }

if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}

# --- STILE ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.5em; }
    .status-box { padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold; margin-bottom: 5px; }
    .occupato { background-color: #e74c3c; }
    .libero { background-color: #2ecc71; }
    .scontrino { background: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd; color: #333; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- HEADER E GESTIONE MENU (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ CONFIGURAZIONE")
    st.subheader("Aggiungi piatto al Menu")
    cat_nuova = st.selectbox("Categoria", list(st.session_state.menu.keys()))
    nome_nuovo = st.text_input("Nome Piatto")
    prezzo_nuovo = st.number_input("Prezzo €", min_value=0.0, step=0.5)
    if st.button("SALVA NEL LISTINO"):
        if nome_nuovo:
            st.session_state.menu[cat_nuova][nome_nuovo] = prezzo_nuovo
            st.success("Aggiunto!")
            st.rerun()

# --- 1. MONITOR TAVOLI (Sempre visibile in alto) ---
st.title("🍹 Domenico Smart Management")
st.subheader("📊 Stato Sala")
cols_tavoli = st.columns(6)
for i, (t_nome, t_items) in enumerate(st.session_state.tavoli.items()):
    stato = "OCCUPATO" if t_items else "LIBERO"
    classe = "occupato" if t_items else "libero"
    cols_tavoli[i % 6].markdown(f"<div class='status-box {classe}'>{t_nome}<br>{stato}</div>", unsafe_allow_html=True)

st.divider()

# --- 2. PUNTO CASSA (Sotto i tavoli) ---
col_ordini, col_conto = st.columns([2, 1])

with col_ordini:
    st.subheader("🛒 Prendi Ordinazione")
    tavolo_attivo = st.selectbox("Gestisci il tavolo:", list(st.session_state.tavoli.keys()))
    
    # Selettore categoria
    cat_scelta = st.radio("Scegli Reparto:", list(st.session_state.menu.keys()), horizontal=True)
    
    st.write(f"Prodotti **{cat_scelta}**:")
    prod_cols = st.columns(3)
    prodotti = st.session_state.menu[cat_scelta]
    for idx, (p_nome, p_prezzo) in enumerate(prodotti.items()):
        if prod_cols[idx % 3].button(f"{p_nome}\n€{p_prezzo:.2f}", key=f"btn_{p_nome}"):
            st.session_state.tavoli[tavolo_attivo].append({"n": p_nome, "p": p_prezzo})
            st.rerun()

with col_conto:
    st.subheader(f"🧾 Conto {tavolo_attivo}")
    items = st.session_state.tavoli[tavolo_attivo]
    
    st.markdown('<div class="scontrino">', unsafe_allow_html=True)
    totale = 0.0
    if not items:
        st.write("Tavolo vuoto.")
    else:
        for item in items:
            st.write(f"{item['n']} <span style='float:right;'>€{item['p']:.2f}</span>", unsafe_allow_html=True)
            totale += item['p']
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"**TOTALE: <span style='float:right;'>€{totale:.2f}</span>**", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")
    c1, c2 = st.columns(2)
    if c1.button("🗑️ SVUOTA"):
        st.session_state.tavoli[tavolo_attivo] = []
        st.rerun()
    if c2.button("💰 PAGA", type="primary"):
        if items:
            st.success("Pagamento registrato!")
            st.balloons()
            st.session_state.tavoli[tavolo_attivo] = []
            st.rerun()
