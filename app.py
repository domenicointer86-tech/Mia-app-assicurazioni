import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Domenico Risto-Pro 2026", layout="wide", page_icon="☕")

# Inizializzazione dati (se non esistono)
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Bar": {"Caffè": 1.20, "Birra": 5.00, "Cornetto": 1.50},
        "Cucina": {"Pizza Margherita": 8.00, "Pasta al Pomodoro": 10.00, "Hamburger": 12.00}
    }
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}
if 'storico_vendite' not in st.session_state:
    st.session_state.storico_vendite = []
if 'magazzino' not in st.session_state:
    st.session_state.magazzino = {"Caffè (kg)": 10, "Birra (unità)": 50, "Farina (kg)": 20}

# --- FUNZIONE STAMPA ---
def genera_scontrino_pdf(tavolo, ordine, totale):
    pdf = FPDF(format=(58, 120))
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "DOMENICO BAR", ln=True, align='C')
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.cell(0, 5, f"Postazione: {tavolo}", ln=True, align='C')
    pdf.cell(0, 5, "-"*25, ln=True, align='C')
    for item in ordine:
        pdf.cell(30, 6, f"{item['n'][:15]}")
        pdf.cell(10, 6, f"€{item['p']:.2f}", ln=True, align='R')
    pdf.cell(0, 5, "-"*25, ln=True, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTALE: €{totale:.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.title("🏢 Gestione Bar")
    scelta = st.radio("VAI A:", ["💰 Cassa & Tavoli", "📦 Magazzino", "📊 Statistiche", "⚙️ Configura Menu"])
    st.divider()
    st.info("Domenico, l'app è pronta per il servizio!")

# --- MODULO 1: CASSA ---
if scelta == "💰 Cassa & Tavoli":
    st.header("💰 Gestione Sala")
    
    # Visualizzazione tavoli rapida
    cols_t = st.columns(6)
    for idx, (t_nome, items) in enumerate(st.session_state.tavoli.items()):
        colore = "🔴" if items else "🟢"
        if cols_t[idx%6].button(f"{colore}\n{t_nome}", key=f"btn_{t_nome}"):
            st.session_state.t_selezionato = t_nome

    if 't_selezionato' in st.session_state:
        t_sel = st.session_state.t_selezionato
        st.divider()
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader(f"🛒 Ordine: {t_sel}")
            for cat, prodotti in st.session_state.menu.items():
                st.write(f"**{cat}**")
                p_cols = st.columns(3)
                for j, (nome, prezzo) in enumerate(prodotti.items()):
                    if p_cols[j%3].button(f"{nome}\n€{prezzo}", key=f"add_{nome}_{t_sel}"):
                        st.session_state.tavoli[t_sel].append({"n": nome, "p": prezzo})
                        st.rerun()
        
        with c2:
            st.subheader("🧾 Scontrino")
            ordine_attuale = st.session_state.tavoli[t_sel]
            totale = sum(item['p'] for item in ordine_attuale)
            
            for i, item in enumerate(ordine_attuale):
                st.write(f"{item['n']} - €{item['p']:.2f}")
            
            st.markdown(f"## TOTALE: €{totale:.2f}")
            
            if totale > 0:
                pdf_sc = genera_scontrino_pdf(t_sel, ordine_attuale, totale)
                st.download_button("🖨️ STAMPA SCONTRINO", pdf_sc, f"scontrino_{t_sel}.pdf", "application/pdf")
                
                if st.button("✅ CHIUDI E INCASSA", type="primary"):
                    st.session_state.storico_vendite.append({"Data": datetime.now(), "Totale": totale})
                    st.session_state.tavoli[t_sel] = []
                    st.balloons()
                    st.rerun()
            if st.button("🗑️ Svuota Tavolo"):
                st.session_state.tavoli[t_sel] = []
                st.rerun()

# --- MODULO 2: MAGAZZINO ---
elif scelta == "📦 Magazzino":
    st.header("📦 Controllo Scorte")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Stato attuale")
        st.table(pd.Series(st.session_state.magazzino, name="Quantità"))
    with col_m2:
        st.subheader("Aggiorna")
        prod_agg = st.selectbox("Prodotto", list(st.session_state.magazzino.keys()))
        nuova_q = st.number_input("Aggiungi quantità", min_value=0)
        if st.button("Carica"):
            st.session_state.magazzino[prod_agg] += nuova_q
            st.success("Caricato!")

# --- MODULO 3: STATISTICHE ---
elif scelta == "📊 Statistiche":
    st.header("📊 Analisi Incassi")
    if st.session_state.storico_vendite:
        df = pd.DataFrame(st.session_state.storico_vendite)
        st.metric("Incasso Totale", f"€ {df['Totale'].sum():.2f}")
        fig = px.bar(df, x="Data", y="Totale", title="Andamento Vendite")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessuna vendita oggi.")

# --- MODULO 4: CONFIGURA MENU ---
elif scelta == "⚙️ Configura Menu":
    st.header("⚙️ Gestione Listino")
    cat_sel = st.selectbox("In quale categoria?", list(st.session_state.menu.keys()))
    nuovo_n = st.text_input("Nome Prodotto (es: Gin Tonic)")
    nuovo_p = st.number_input("Prezzo (€)", min_value=0.0, step=0.50)
    if st.button("Aggiungi al Listino"):
        st.session_state.menu[cat_sel][nuovo_n] = nuovo_p
        st.success(f"{nuovo_n} aggiunto!")
