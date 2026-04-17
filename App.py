import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE INIZIALE ---
st.set_page_config(page_title="Domenico Risto-Pro 2026", layout="wide", page_icon="🍴")

# --- DATABASE IN MEMORIA (Session State) ---
if 'setup_done' not in st.session_state:
    st.session_state.menu = {
        "ANTIPASTI": {"Tagliere Misto": 15.0, "Bruschette": 6.0},
        "PRIMI": {"Carbonara": 12.0, "Amatriciana": 11.0},
        "PIZZE": {"Margherita": 7.0, "Diavola": 8.5},
        "BAR/BEVANDE": {"Caffè": 1.2, "Birra 0.4": 5.0, "Vino Calice": 4.0},
        "DOLCI": {"Tiramisù": 5.0, "Panna Cotta": 4.5}
    }
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 21)}
    st.session_state.incasso_totale = 0.0
    st.session_state.log_vendite = []
    st.session_state.setup_done = True

# --- STILE CSS PROFESSIONALE ---
st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3.5em; }
    .tavolo-libero { background-color: #2ecc71; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    .tavolo-occupato { background-color: #e74c3c; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    .card-cassa { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .sidebar-header { color: #1e3d59; font-weight: bold; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: NAVIGAZIONE E GESTIONE MENU ---
with st.sidebar:
    st.markdown("<div class='sidebar-header'>ADMIN PANEL</div>", unsafe_allow_html=True)
    menu_opzione = st.radio("Vai a:", ["🖥️ Dashboard Sala", "💰 Punto Cassa", "⚙️ Gestione Menu", "📈 Report Incassi"])
    
    st.divider()
    if menu_opzione == "⚙️ Gestione Menu":
        st.subheader("Aggiungi Prodotto")
        cat_agg = st.selectbox("Categoria", list(st.session_state.menu.keys()))
        nome_agg = st.text_input("Nome Piatto")
        prezzo_agg = st.number_input("Prezzo €", min_value=0.0, step=0.5)
        if st.button("SALVA NEL LISTINO"):
            if nome_agg:
                st.session_state.menu[cat_agg][nome_agg] = prezzo_agg
                st.success("Listino aggiornato!")
                st.rerun()

# --- 1. DASHBOARD SALA ---
if menu_opzione == "🖥️ Dashboard Sala":
    st.title("🖥️ Stato Sala in Tempo Reale")
    cols = st.columns(5)
    for i, (t_nome, t_ordini) in enumerate(st.session_state.tavoli.items()):
        stato = "LIBERO" if not t_ordini else f"OCCUPATO (€{sum(item['p'] for item in t_ordini):.2f})"
        classe = "tavolo-libero" if not t_ordini else "tavolo-occupato"
        cols[i % 5].markdown(f"<div class='{classe}'><b>{t_nome}</b><br>{stato}</div>", unsafe_allow_html=True)
        st.write("") # Spaziatore

# --- 2. PUNTO CASSA ---
elif menu_opzione == "💰 Punto Cassa":
    st.title("💰 Punto Cassa Touch")
    
    col_sx, col_dx = st.columns([2, 1])
    
    with col_sx:
        tavolo_attivo = st.selectbox("Seleziona Tavolo da servire", list(st.session_state.tavoli.keys()))
        
        # Tabs per le categorie del menu
        categorie = list(st.session_state.menu.keys())
        tabs = st.tabs(categorie)
        
        for i, cat_nome in enumerate(categorie):
            with tabs[i]:
                prodotti = st.session_state.menu[cat_nome]
                p_cols = st.columns(3)
                for j, (p_nome, p_prezzo) in enumerate(prodotti.items()):
                    if p_cols[j % 3].button(f"{p_nome}\n€{p_prezzo:.2f}", key=f"cassa_{cat_nome}_{p_nome}"):
                        st.session_state.tavoli[tavolo_attivo].append({"n": p_nome, "p": p_prezzo, "t": datetime.now().strftime("%H:%M")})
                        st.rerun()

    with col_dx:
        st.markdown(f"### 🧾 Conto {tavolo_attivo}")
        ordini_tavolo = st.session_state.tavoli[tavolo_attivo]
        
        st.markdown("<div class='card-cassa'>", unsafe_allow_html=True)
        totale_tavolo = 0.0
        if not ordini_tavolo:
            st.write("Nessun articolo.")
        else:
            for item in ordini_tavolo:
                st.write(f"**{item['n']}** <span style='float:right;'>€{item['p']:.2f}</span>", unsafe_allow_html=True)
                totale_tavolo += item['p']
            
            st.divider()
            st.markdown(f"### TOTALE: €{totale_tavolo:.2f}")
            
            if st.button("🔥 STAMPA COMANDA (Invia a Cucina)"):
                st.info("Comanda inviata ai reparti!")
                
            if st.button("✅ CHIUDI CONTO (Pagato)", type="primary"):
                st.session_state.incasso_totale += totale_tavolo
                st.session_state.log_vendite.append({"tavolo": tavolo_attivo, "totale": totale_tavolo, "ora": datetime.now().strftime("%H:%M")})
                st.session_state.tavoli[tavolo_attivo] = []
                st.balloons()
                st.success("Tavolo liberato e incasso registrato!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. REPORT INCASSI ---
elif menu_opzione == "📈 Report Incassi":
    st.title("📈 Analisi Vendite")
    st.metric("INCASSO TOTALE ODIERNO", f"€ {st.session_state.incasso_totale:.2f}")
    
    if st.session_state.log_vendite:
        df = pd.DataFrame(st.session_state.log_vendite)
        st.table(df)
        
        if st.button("🗑️ AZZERA GIORNATA (Chiusura Fiscale)"):
            st.session_state.incasso_totale = 0.0
            st.session_state.log_vendite = []
            st.warning("Giornata azzerata!")
            st.rerun()
    else:
        st.write("Nessuna vendita registrata oggi.")

st.markdown("<br><hr><center><small>Domenico Risto-Pro v3.0 | Sistema Gestione Avanzata</small></center>", unsafe_allow_html=True)
