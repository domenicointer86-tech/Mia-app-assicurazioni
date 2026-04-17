import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE E SESSIONE ---
st.set_page_config(page_title="DOMENICO ULTRA-PRO", layout="wide", page_icon="🏢")

if 'init' not in st.session_state:
    st.session_state.menu = {
        "Cucina": {"Pizza": 8.0, "Pasta": 10.0, "Carne": 15.0},
        "Bar": {"Caffè": 1.2, "Birra": 5.0, "Cocktail": 7.0}
    }
    st.session_state.magazzino = {"Birra": 50, "Caffè": 100, "Pasta": 20}
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 16)}
    st.session_state.vendite_storico = []
    st.session_state.camerieri = ["Domenico", "Staff 1", "Staff 2"]
    st.session_state.init = True

# --- CSS LUXURY DARK ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { border-radius: 10px; height: 3em; font-weight: bold; }
    .metric-card { background: #1c1f26; padding: 15px; border-radius: 10px; border-left: 5px solid #c5a059; }
    .stTab { background-color: transparent !important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.title("🏢 BUSINESS PANEL")
    scelta = st.radio("VAI A:", [
        "💰 CASSA & TAVOLI", 
        "📦 MAGAZZINO", 
        "📊 STATISTICHE VENDITE", 
        "⚙️ CONFIGURAZIONE MENU"
    ])
    st.divider()
    user = st.selectbox("OPERATORE:", st.session_state.camerieri)

# --- MODULO 1: CASSA & TAVOLI ---
if scelta == "💰 CASSA & TAVOLI":
    st.header(f"💰 Punto Vendita - Operatore: {user}")
    
    # Grid Tavoli Rapida
    t_cols = st.columns(5)
    for i, (t_nome, t_items) in enumerate(st.session_state.tavoli.items()):
        color = "🔴" if t_items else "🟢"
        if t_cols[i % 5].button(f"{color} {t_nome}", key=f"select_{t_nome}"):
            st.session_state.tavolo_attivo = t_nome

    st.divider()

    if 'tavolo_attivo' in st.session_state:
        t_sel = st.session_state.tavolo_attivo
        col_dx, col_sx = st.columns([2, 1])
        
        with col_dx:
            st.subheader(f"🛒 Ordine {t_sel}")
            tabs = st.tabs(list(st.session_state.menu.keys()))
            for i, cat in enumerate(st.session_state.menu.keys()):
                with tabs[i]:
                    m_cols = st.columns(3)
                    prodotti = st.session_state.menu[cat]
                    for j, (p, prezzo) in enumerate(prodotti.items()):
                        if m_cols[j % 3].button(f"{p}\n€{prezzo}", key=f"add_{p}_{t_sel}"):
                            st.session_state.tavoli[t_sel].append({"p": p, "pr": prezzo, "ora": datetime.now().strftime("%H:%M")})
                            # Scarico magazzino automatico se esiste il prodotto
                            if p in st.session_state.magazzino:
                                st.session_state.magazzino[p] -= 1
                            st.rerun()

        with col_sx:
            st.subheader("🧾 Scontrino")
            ordine = st.session_state.tavoli[t_sel]
            totale = sum(item['pr'] for item in ordine)
            for item in ordine:
                st.write(f"{item['p']} - €{item['pr']}")
            st.markdown(f"## TOTALE: €{totale:.2f}")
            
            if st.button("✅ CHIUDI E INCASSA", type="primary"):
                if ordine:
                    st.session_state.vendite_storico.append({
                        "Data": datetime.now().strftime("%Y-%m-%d"),
                        "Ora": datetime.now().strftime("%H:%M"),
                        "Tavolo": t_sel,
                        "Totale": totale,
                        "Cameriere": user
                    })
                    st.session_state.tavoli[t_sel] = []
                    st.balloons()
                    st.rerun()

# --- MODULO 2: MAGAZZINO ---
elif scelta == "📦 MAGAZZINO":
    st.header("📦 Gestione Scorte")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Stato Attuale")
        for prod, qta in st.session_state.magazzino.items():
            colore_qta = "orange" if qta < 10 else "white"
            st.markdown(f"**{prod}**: <span style='color:{colore_qta};'>{qta} unità</span>", unsafe_allow_html=True)
    with col_m2:
        st.subheader("Carico Merci")
        p_carico = st.selectbox("Prodotto", list(st.session_state.magazzino.keys()))
        q_carico = st.number_input("Quantità da aggiungere", min_value=1)
        if st.button("AGGIORNA SCORTE"):
            st.session_state.magazzino[p_carico] += q_carico
            st.success("Magazzino aggiornato!")
            st.rerun()

# --- MODULO 3: STATISTICHE ---
elif scelta == "📊 STATISTICHE VENDITE":
    st.header("📊 Analisi Aziendale")
    if st.session_state.vendite_storico:
        df = pd.DataFrame(st.session_state.vendite_storico)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Incasso Lordo", f"€ {df['Totale'].sum():.2f}")
        c2.metric("Ordini Chiusi", len(df))
        c3.metric("Media Scontrino", f"€ {df['Totale'].mean():.2f}")
        
        st.subheader("Andamento Vendite")
        fig = px.line(df, x="Ora", y="Totale", title="Vendite per Orario", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Performance Staff")
        fig2 = px.bar(df, x="Cameriere", y="Totale", color="Cameriere", title="Incasso per Operatore")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Ancora nessuna vendita registrata oggi.")

# --- MODULO 4: CONFIGURAZIONE ---
elif scelta == "⚙️ CONFIGURAZIONE MENU":
    st.header("⚙️ Configurazione Sistema")
    with st.expander("Modifica Menu"):
        c1, c2, c3 = st.columns(3)
        nuova_cat = c1.selectbox("Categoria", list(st.session_state.menu.keys()))
        nuovo_p = c2.text_input("Nome Piatto")
        nuovo_pr = c3.number_input("Prezzo €", min_value=0.0)
        if st.button("AGGIUNGI AL LISTINO"):
            st.session_state.menu[nuova_cat][nuovo_p] = nuovo_pr
            # Inizializza anche nel magazzino
            st.session_state.magazzino[nuovo_p] = 0
            st.rerun()
