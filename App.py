import streamlit as st
from datetime import datetime
try:
    from fpdf import FPDF
    PDF_SUPPORT = True
except:
    PDF_SUPPORT = False

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="HORECA PRO - FOTO MENU", layout="wide", page_icon="🖼️")

# CSS PER BOTTONI CON IMMAGINI
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { 
        border-radius: 12px; 
        height: 100px; 
        font-weight: 700; 
        font-size: 15px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        white-space: pre-wrap; /* Permette il ritorno a capo per l'emoji */
    }
    .cat-header { background-color: #2c3e50; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATI ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "☕ CAFFETTERIA": {
            "Caffè": {"p": 1.2, "img": "☕"}, 
            "Cappuccino": {"p": 1.8, "img": "🥛"},
            "Cornetto": {"p": 1.5, "img": "🥐"}
        },
        "🍷 BEVANDE": {
            "Acqua": {"p": 1.0, "img": "💧"}, 
            "Birra": {"p": 3.5, "img": "🍺"},
            "Coca Cola": {"p": 3.0, "img": "🥤"}
        }
    }
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"TAVOLO {i}": [] for i in range(1, 13)}
if 'incasso' not in st.session_state:
    st.session_state.incasso = 0.0

# --- SEZIONE 1: SALA TAVOLI (CON GRAFICA) ---
with st.sidebar:
    st.title("🏨 HORECA PRO")
    scelta = st.radio("MENU PRINCIPALE", ["🛎️ SALA TAVOLI", "⚙️ GESTIONE LISTINO", "📊 CHIUSURA CASSA"])
    st.divider()
    st.metric("INCASSO OGGI", f"€ {st.session_state.incasso:.2f}")

if scelta == "🛎️ SALA TAVOLI":
    st.subheader("📍 Selezione Tavolo")
    t_cols = st.columns(4)
    for i, (t_nome, items) in enumerate(st.session_state.tavoli.items()):
        label = f"{t_nome}\n€{sum(x['p'] for x in items):.2f}" if items else f"{t_nome}\n(LIBERO)"
        if t_cols[i%4].button(label, key=t_nome, type="primary" if items else "secondary"):
            st.session_state.t_attivo = t_nome

    if 't_attivo' in st.session_state:
        t_sel = st.session_state.t_attivo
        st.divider()
        c_menu, c_conto = st.columns([2, 1])

        with c_menu:
            st.markdown(f"<div class='cat-header'>SELEZIONE VISIVA - {t_sel}</div>", unsafe_allow_html=True)
            tabs = st.tabs(list(st.session_state.menu.keys()))
            for i, cat in enumerate(st.session_state.menu.keys()):
                with tabs[i]:
                    m_cols = st.columns(3)
                    for j, (prod, dati) in enumerate(st.session_state.menu[cat].items()):
                        # Mostriamo Emoji + Nome + Prezzo sul bottone
                        testo_bottone = f"{dati['img']}\n{prod}\n€{dati['p']:.2f}"
                        if m_cols[j%3].button(testo_bottone, key=f"add_{cat}_{prod}"):
                            st.session_state.tavoli[t_sel].append({"n": prod, "p": dati['p']})
                            st.rerun()

        with c_conto:
            st.markdown(f"<div class='cat-header' style='background-color:#e67e22;'>CONTO {t_sel}</div>", unsafe_allow_html=True)
            ordine = st.session_state.tavoli[t_sel]
            tot = sum(x['p'] for x in ordine)
            for idx, item in enumerate(ordine):
                c_n, c_p, c_d = st.columns([3, 2, 1])
                c_n.write(item['n'])
                c_p.write(f"€{item['p']:.2f}")
                if c_d.button("X", key=f"del_{idx}"):
                    st.session_state.tavoli[t_sel].pop(idx)
                    st.rerun()
            st.divider()
            st.markdown(f"## TOTALE: €{tot:.2f}")
            if tot > 0:
                if st.button("✅ CHIUDI E INCASSA", type="primary", use_container_width=True):
                    st.session_state.incasso += tot
                    st.session_state.tavoli[t_sel] = []
                    st.success("Tavolo chiuso!")
                    st.rerun()

# --- SEZIONE 2: GESTIONE LISTINO (CON AGGIUNTA FOTO/EMOJI) ---
elif scelta == "⚙️ GESTIONE LISTINO":
    st.header("⚙️ Configura Prodotti con Icone")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    categoria = col_a.selectbox("Categoria", list(st.session_state.menu.keys()) + ["NUOVA CATEGORIA"])
    if categoria == "NUOVA CATEGORIA":
        categoria = col_a.text_input("Nome Categoria").upper()
    
    nome = col_b.text_input("Nome Prodotto")
    prezzo = col_c.number_input("Prezzo (€)", min_value=0.0, step=0.10)
    icona = col_d.text_input("Icona/Emoji (es: 🍹, 🍕, 🍔)")
    
    if st.button("SALVA NEL LISTINO"):
        if categoria not in st.session_state.menu:
            st.session_state.menu[categoria] = {}
        st.session_state.menu[categoria][nome] = {"p": prezzo, "img": icona if icona else "📦"}
        st.success("Prodotto aggiunto con successo!")
        st.rerun()

    st.divider()
    for cat, prods in st.session_state.menu.items():
        with st.expander(f"LISTINO {cat}"):
            for p, dati in prods.items():
                st.write(f"{dati['img']} {p}: €{dati['p']:.2f}")

# --- SEZIONE 3: CHIUSURA ---
elif scelta == "📊 CHIUSURA CASSA":
    st.header("📊 Resoconto")
    st.metric("INCASSO TOTALE", f"€ {st.session_state.incasso:.2f}")
    if st.button("🔴 RESET GIORNATA"):
        st.session_state.incasso = 0.0
        st.rerun()
