import streamlit as st
from datetime import datetime
try:
    from fpdf import FPDF
    PDF_SUPPORT = True
except:
    PDF_SUPPORT = False

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="HORECA PRO - DOMENICO", layout="wide", page_icon="🏨")

# CSS PER STILE PROFESSIONALE (Horeca Manager Style)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { border-radius: 10px; height: 70px; font-weight: 700; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .cat-header { background-color: #2c3e50; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 15px; }
    .sidebar .sidebar-content { background-color: #1a252f; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATI ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "☕ CAFFETTERIA": {"Caffè": 1.2, "Cappuccino": 1.8, "Cornetto": 1.5},
        "🍷 BEVANDE": {"Acqua": 1.0, "Birra": 3.5, "Coca Cola": 3.0},
        "🍔 RISTORAZIONE": {"Toast": 4.5, "Hamburger": 8.0}
    }
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"TAVOLO {i}": [] for i in range(1, 13)}
if 'incasso' not in st.session_state:
    st.session_state.incasso = 0.0

# --- FUNZIONE SCONTRINO ---
def genera_scontrino(tavolo, ordine, totale):
    pdf = FPDF(format=(58, 100))
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "DOMENICO BAR", ln=True, align='C')
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Tavolo: {tavolo}", ln=True, align='C')
    pdf.cell(0, 5, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True, align='C')
    pdf.cell(0, 5, "-"*30, ln=True, align='C')
    for item in ordine:
        pdf.cell(30, 6, f"{item['n']}")
        pdf.cell(10, 6, f"€{item['p']:.2f}", ln=True, align='R')
    pdf.cell(0, 5, "-"*30, ln=True, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTALE: €{totale:.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏨 HORECA PRO")
    scelta = st.radio("MENU PRINCIPALE", ["🛎️ SALA TAVOLI", "⚙️ GESTIONE LISTINO", "📊 CHIUSURA CASSA"])
    st.divider()
    st.metric("INCASSO OGGI", f"€ {st.session_state.incasso:.2f}")

# --- SEZIONE 1: SALA TAVOLI ---
if scelta == "🛎️ SALA TAVOLI":
    st.subheader("📍 Piantina Sala")
    t_cols = st.columns(4)
    for i, (t_nome, items) in enumerate(st.session_state.tavoli.items()):
        color = "primary" if items else "secondary"
        label = f"{t_nome}\n€{sum(x['p'] for x in items):.2f}" if items else f"{t_nome}\n(LIBERO)"
        if t_cols[i%4].button(label, key=t_nome, type=color):
            st.session_state.t_attivo = t_nome

    if 't_attivo' in st.session_state:
        t_sel = st.session_state.t_attivo
        st.divider()
        c_menu, c_conto = st.columns([2, 1])

        with c_menu:
            st.markdown(f"<div class='cat-header'>MENU PRODOTTI - {t_sel}</div>", unsafe_allow_html=True)
            tabs = st.tabs(list(st.session_state.menu.keys()))
            for i, cat in enumerate(st.session_state.menu.keys()):
                with tabs[i]:
                    m_cols = st.columns(3)
                    for j, (prod, prezzo) in enumerate(st.session_state.menu[cat].items()):
                        if m_cols[j%3].button(f"{prod}\n€{prezzo:.2f}", key=f"add_{cat}_{prod}"):
                            st.session_state.tavoli[t_sel].append({"n": prod, "p": prezzo})
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
                if PDF_SUPPORT:
                    pdf_data = genera_scontrino(t_sel, ordine, tot)
                    st.download_button("🖨️ STAMPA SCONTRINO", pdf_data, f"scontrino_{t_sel}.pdf", "application/pdf", use_container_width=True)
                
                if st.button("✅ CHIUDI E INCASSA", type="primary", use_container_width=True):
                    st.session_state.incasso += tot
                    st.session_state.tavoli[t_sel] = []
                    st.success("Tavolo chiuso!")
                    st.rerun()

# --- SEZIONE 2: GESTIONE LISTINO ---
elif scelta == "⚙️ GESTIONE LISTINO":
    st.header("⚙️ Configura il tuo Menu")
    col_a, col_b, col_c = st.columns(3)
    cat_lista = list(st.session_state.menu.keys())
    categoria = col_a.selectbox("Categoria", cat_lista + ["NUOVA CATEGORIA"])
    if categoria == "NUOVA CATEGORIA":
        categoria = col_a.text_input("Nome categoria").upper()
    
    nuovo_nome = col_b.text_input("Nome Prodotto")
    nuovo_prezzo = col_c.number_input("Prezzo (€)", min_value=0.0, step=0.10)
    
    if st.button("AGGIUNGI AL LISTINO"):
        if categoria not in st.session_state.menu:
            st.session_state.menu[categoria] = {}
        st.session_state.menu[categoria][nuovo_nome] = nuovo_prezzo
        st.success("Aggiunto!")
        st.rerun()

    st.divider()
    for cat, prods in st.session_state.menu.items():
        with st.expander(f"MODIFICA {cat}"):
            for p, pr in list(prods.items()):
                c1, c2 = st.columns([4, 1])
                c1.write(f"{p}: €{pr:.2f}")
                if c2.button("Elimina", key=f"rm_{cat}_{p}"):
                    del st.session_state.menu[cat][p]
                    st.rerun()

# --- SEZIONE 3: CHIUSURA ---
elif scelta == "📊 CHIUSURA CASSA":
    st.header("📊 Resoconto")
    st.metric("INCASSO TOTALE", f"€ {st.session_state.incasso:.2f}")
    if st.button("🔴 RESET GIORNATA"):
        st.session_state.incasso = 0.0
        st.rerun()
