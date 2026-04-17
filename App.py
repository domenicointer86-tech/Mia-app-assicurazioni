import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="DOMENICO LUXURY BAR", layout="wide", page_icon="🍸")

# CSS personalizzato per renderlo elegante
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2e2e2e; color: white; border: 1px solid #4a4a4a; }
    .stButton>button:hover { background-color: #4a4a4a; border-color: #ff4b4b; }
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATI ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "☕ CAFFETTERIA": {"Caffè": 1.2, "Cappuccino": 1.8, "Cornetto": 1.5, "Tè": 2.5},
        "🍺 BEVANDE": {"Birra Spina 0.4": 5.0, "Coca Cola": 3.0, "Acqua 0.5": 1.0, "Succo": 2.5},
        "🍸 COCKTAIL": {"Spritz": 6.0, "Gin Tonic": 8.0, "Negroni": 7.0, "Mojito": 7.5},
        "🥪 FOOD": {"Toast": 4.5, "Panino Crudo": 6.0, "Pizzetta": 3.5}
    }
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}
if 'incasso_totale' not in st.session_state:
    st.session_state.incasso_totale = 0.0

# --- FUNZIONI ---
def genera_scontrino(tavolo, ordine, totale):
    pdf = FPDF(format=(58, 100))
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "DOMENICO LUXURY BAR", ln=True, align='C')
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 4, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.cell(0, 4, f"Postazione: {tavolo}", ln=True, align='C')
    pdf.cell(0, 5, "-"*30, ln=True, align='C')
    for item in ordine:
        pdf.cell(25, 5, f"{item['n']}")
        pdf.cell(10, 5, f"€{item['p']:.2f}", ln=True, align='R')
    pdf.cell(0, 5, "-"*30, ln=True, align='C')
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, f"TOTALE: €{totale:.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3170/3170733.png", width=100)
    st.title("DOMENICO PRO")
    menu_nav = st.radio("Scegli Sezione:", ["🛎️ SALA TAVOLI", "📦 MAGAZZINO & MENU", "📊 FINE GIORNATA"])
    st.divider()
    st.metric("INCASSO OGGI", f"€ {st.session_state.incasso_totale:.2f}")

# --- SEZIONE 1: SALA TAVOLI ---
if menu_nav == "🛎️ SALA TAVOLI":
    st.title("🛎️ Gestione Sala")
    
    # Griglia Tavoli
    cols = st.columns(4)
    for i, (t_nome, items) in enumerate(st.session_state.tavoli.items()):
        stato = "🔴 OCCUPATO" if items else "🟢 LIBERO"
        if cols[i % 4].button(f"{t_nome}\n{stato}", key=f"btn_{t_nome}"):
            st.session_state.t_attivo = t_nome
            
    if 't_attivo' in st.session_state:
        t_sel = st.session_state.t_attivo
        st.divider()
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader(f"🛒 Ordinazione {t_sel}")
            tabs = st.tabs(list(st.session_state.menu.keys()))
            for i, cat in enumerate(st.session_state.menu.keys()):
                with tabs[i]:
                    m_cols = st.columns(3)
                    for j, (prod, prezzo) in enumerate(st.session_state.menu[cat].items()):
                        if m_cols[j % 3].button(f"{prod}\n€{prezzo}", key=f"add_{prod}_{t_sel}"):
                            st.session_state.tavoli[t_sel].append({"n": prod, "p": prezzo})
                            st.rerun()
        
        with c2:
            st.subheader("🧾 Conto")
            ordine_corrente = st.session_state.tavoli[t_sel]
            tot = sum(x['p'] for x in ordine_corrente)
            for item in ordine_corrente:
                st.write(f"• {item['n']} - €{item['p']:.2f}")
            st.divider()
            st.markdown(f"### TOTALE: €{tot:.2f}")
            
            if tot > 0:
                # Tasto Stampa
                pdf_bytes = genera_scontrino(t_sel, ordine_corrente, tot)
                st.download_button("🖨️ STAMPA PROMEMORIA", pdf_bytes, f"conto_{t_sel}.pdf", "application/pdf")
                
                if st.button("💰 CHIUDI CONTO (INCASSA)", type="primary"):
                    st.session_state.incasso_totale += tot
                    st.session_state.tavoli[t_sel] = []
                    st.success("Tavolo liberato e incasso registrato!")
                    st.rerun()
            if st.button("🗑️ Svuota Tavolo"):
                st.session_state.tavoli[t_sel] = []
                st.rerun()

# --- SEZIONE 2: MAGAZZINO & MENU ---
elif menu_nav == "📦 MAGAZZINO & MENU":
    st.title("📦 Gestione Listino")
    cat_sel = st.selectbox("Seleziona Categoria", list(st.session_state.menu.keys()))
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        nuovo_n = st.text_input("Nome Prodotto")
        nuovo_p = st.number_input("Prezzo (€)", min_value=0.0, step=0.10)
        if st.button("➕ Aggiungi al Menu"):
            st.session_state.menu[cat_sel][nuovo_n] = nuovo_p
            st.success("Menu aggiornato!")
    with col_m2:
        st.write("**Prodotti attuali:**")
        for p, pr in st.session_state.menu[cat_sel].items():
            st.write(f"- {p}: €{pr:.2f}")

# --- SEZIONE 3: FINE GIORNATA ---
elif menu_nav == "📊 FINE GIORNATA":
    st.title("📊 Resoconto Giornaliero")
    st.metric("INCASSO TOTALE", f"€ {st.session_state.incasso_totale:.2f}")
    if st.button("🔴 AZZERA GIORNATA (CHIUSURA)"):
        st.session_state.incasso_totale = 0.0
        st.warning("Incasso azzerato per la nuova giornata.")
        st.rerun()
