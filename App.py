import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE E SESSIONE ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Caffetteria": {"Caffè": 1.2, "Cappuccino": 1.5, "Cornetto": 1.2},
        "Bevande": {"Birra": 4.0, "Spritz": 5.0, "Acqua": 1.5},
        "Cucina": {"Panino": 6.5, "Tagliere": 12.0, "Primo del Giorno": 10.0}
    }
if 'ordini_tavoli' not in st.session_state:
    st.session_state.ordini_tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}

st.set_page_config(page_title="Domenico PRO Management", layout="wide", page_icon="🍹")

# --- CSS CUSTOM PER INTERFACCIA PROFESSIONALE ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1e2d3b; color: white; }
    .tavolo-card {
        padding: 20px; border-radius: 15px; text-align: center;
        font-weight: bold; margin: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .occupato { background-color: #e74c3c; color: white; }
    .libero { background-color: #2ecc71; color: white; }
    .scontrino-font { font-family: 'Courier New', monospace; background: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: GESTIONE MENU ---
with st.sidebar:
    st.title("⚙️ SETTINGS")
    st.subheader("Aggiungi Pietanza")
    cat_nuova = st.selectbox("Categoria", list(st.session_state.menu.keys()))
    nome_nuovo = st.text_input("Nome Piatto")
    prezzo_nuovo = st.number_input("Prezzo €", min_value=0.0, step=0.5)
    if st.button("➕ AGGIUNGI AL MENU"):
        if nome_nuovo:
            st.session_state.menu[cat_nuova][nome_nuovo] = prezzo_nuovo
            st.success(f"{nome_nuovo} aggiunto!")
            st.rerun()
    
    st.markdown("---")
    st.write("📩 Email invio: `domenicointer86@gmail.com`")

# --- AREA PRINCIPALE ---
st.title("🚀 Domenico Smart Management")

# Sezione Stato Sala (Visuale Rapida)
st.subheader("📊 Stato Sala")
cols_sala = st.columns(6)
for i, (t_nome, t_items) in enumerate(st.session_state.ordini_tavoli.items()):
    col_idx = i % 6
    stato_classe = "occupato" if t_items else "libero"
    testo_stato = "OCCUPATO" if t_items else "LIBERO"
    cols_sala[col_idx].markdown(f"<div class='tavolo-card {stato_classe}'>{t_nome}<br><small>{testo_stato}</small></div>", unsafe_allow_html=True)

st.markdown("---")

# Sezione Operativa: Presa Ordine e Conto
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🛒 Prendi Comanda")
    tavolo_attivo = st.selectbox("Seleziona Tavolo da servire", list(st.session_state.ordini_tavoli.keys()))
    
    cat_scelta = st.radio("Seleziona Reparto", list(st.session_state.menu.keys()), horizontal=True)
    
    st.write(f"**Prodotti {cat_scelta}:**")
    p_cols = st.columns(3)
    prodotti = st.session_state.menu[cat_scelta]
    for idx, (p_nome, p_prezzo) in enumerate(prodotti.items()):
        if p_cols[idx % 3].button(f"{p_nome}\n€{p_prezzo:.2f}", key=f"{tavolo_attivo}_{p_nome}", use_container_width=True):
            st.session_state.ordini_tavoli[tavolo_attivo].append({"prodotto": p_nome, "prezzo": p_prezzo})
            st.toast(f"Aggiunto {p_nome}")
            st.rerun()

with col_right:
    st.subheader(f"🧾 Conto {tavolo_attivo}")
    items = st.session_state.ordini_tavoli[tavolo_attivo]
    
    with st.container():
        st.markdown('<div class="scontrino-font">', unsafe_allow_html=True)
        totale = 0.0
        if not items:
            st.write("Nessun ordine presente.")
        else:
            for item in items:
                st.write(f"{item['prodotto']} <span style='float:right;'>€{item['prezzo']:.2f}</span>", unsafe_allow_html=True)
                totale += item['prezzo']
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"**TOTALE <span style='float:right; font-size:20px;'>€{totale:.2f}</span>**", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    if c1.button("🗑️ SVUOTA", use_container_width=True):
        st.session_state.ordini_tavoli[tavolo_attivo] = []
        st.rerun()
        
    if c2.button("💰 CHIUDI", type="primary", use_container_width=True):
        if items:
            st.balloons()
            # Logica invio Email (FormSubmit)
            dettaglio_mail = "\n".join([f"{i['prodotto']}: €{i['prezzo']}" for i in items])
            form_html = f"""
                <form action="https://formsubmit.co/domenicointer86@gmail.com" method="POST" id="checkout">
                    <input type="hidden" name="Tavolo" value="{tavolo_attivo}">
                    <input type="hidden" name="Ordine" value="{dettaglio_mail}">
                    <input type="hidden" name="Totale" value="€ {totale:.2f}">
                </form>
                <script>document.getElementById('checkout').submit();</script>
            """
            st.components.v1.html(form_html, height=0)
            st.session_state.ordini_tavoli[tavolo_attivo] = []
            st.success("Conto Chiuso!")
            st.rerun()

st.markdown("<br><p style='text-align:center; color:silver;'>Domenico PRO Management v2.0 - 2026</p>", unsafe_allow_html=True)
