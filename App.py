import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIGURAZIONE DATABASE ---
conn = sqlite3.connect('ristopro_completo.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vendite 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)''')
conn.commit()

# --- 2. FUNZIONE PDF (CORRETTA PER UNICODE) ---
def crea_pdf(tavolo, piatti, totale):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"RICEVUTA - {tavolo}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(10)
    for p in piatti:
        # Pulizia caratteri speciali per evitare UnicodeEncodeError
        nome = p['nome'].replace('à','a').replace('è','e').replace('é','e').replace('ì','i').replace('ò','o').replace('ù','u')
        pdf.cell(150, 10, txt=f"{nome}", border=1)
        pdf.cell(40, 10, txt=f"{p['prezzo']} Euro", border=1, ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"TOTALE: {totale} Euro", ln=True)
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- 3. INIZIALIZZAZIONE SESSIONE ---
if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 11)}

menu_ristorante = {
    "Primi": {"Carbonara": 12.0, "Lasagna": 10.0, "Gnocchi": 9.0},
    "Secondi": {"Tagliata": 18.0, "Orata": 15.0, "Cotoletta": 13.0},
    "Pizze": {"Margherita": 7.0, "Diavola": 8.5, "Napoli": 8.0},
    "Drink": {"Birra": 5.0, "Vino": 4.0, "Acqua": 2.0, "Caffe": 1.5}
}

# --- 4. LOGICA DI ACCESSO ---
if not st.session_state.autenticato:
    st.title("🔐 RistoPro - Accesso")
    pwd = st.text_input("Password", type="password")
    if st.button("Entra"):
        if pwd == "admin123":
            st.session_state.autenticato = True
            st.rerun()
        else:
            st.error("Password errata")
else:
    # --- 5. INTERFACCIA PRINCIPALE ---
    st.sidebar.title("🍽️ RistoPro v3.1")
    app_mode = st.sidebar.selectbox("Vai a:", ["Gestione Sala", "Vista Cucina", "Dashboard Incassi"])

    if app_mode == "Gestione Sala":
        st.header("📍 Mappa Tavoli e Ordini")
        
        # Griglia Tavoli (Visiva)
        cols = st.columns(5)
        for i, (t, p) in enumerate(st.session_state.tavoli.items()):
            color = "🔴" if p else "🟢"
            cols[i%5].button(f"{color} {t}", key=f"btn_{t}")

        st.divider()

        col_ord, col_conto = st.columns(2)
        
        with col_ord:
            st.subheader("📝 Nuovo Ordine")
            t_sel = st.selectbox("Seleziona Tavolo", list(st.session_state.tavoli.keys()))
            cat_sel = st.selectbox("Categoria", list(menu_ristorante.keys()))
            piatto_sel = st.selectbox("Piatto", list(menu_ristorante[cat_sel].keys()))
            
            if st.button("Invia in Cucina 🚀"):
                st.session_state.tavoli[t_sel].append({"nome": piatto_sel, "prezzo": menu_ristorante[cat_sel][piatto_sel]})
                st.success(f"{piatto_sel} aggiunto al {t_sel}")

        with col_conto:
            st.subheader(f"💰 Conto {t_sel}")
            ordini_attuali = st.session_state.tavoli[t_sel]
            if ordini_attuali:
                df = pd.DataFrame(ordini_attuali)
                st.table(df)
                totale = df['prezzo'].sum()
                st.write(f"### Totale: {totale}€")
                
                # Scarica PDF
                pdf_bytes = crea_pdf(t_sel, ordini_attuali, totale)
                st.download_button("🖨️ Stampa Scontrino", data=pdf_bytes, file_name=f"conto_{t_sel}.pdf")
                
                if st.button("Paga e Libera"):
                    piatti_str = ", ".join([p['nome'] for p in ordini_attuali])
                    c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                              (t_sel, piatti_str, totale, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    st.session_state.tavoli[t_sel] = []
                    st.success("Tavolo Liberato!")
                    st.rerun()
            else:
                st.info("Nessun ordine pendente.")

    elif app_mode == "Vista Cucina":
        st.header("👨‍🍳 Comande da Preparare")
        for t, p in st.session_state.tavoli.items():
            if p:
                with st.expander(f"ORDINE {t}", expanded=True):
                    for item in p:
                        st.write(f"- {item['nome']}")
                    if st.button(f"Segna Pronto {t}"):
                        st.balloons()
                        st.info(f"Cameriere avvisato per il {t}")

    elif app_mode == "Dashboard Incassi":
        st.header("📊 Analisi Vendite")
        df_vendite = pd.read_sql_query("SELECT * FROM vendite", conn)
        if not df_vendite.empty:
            st.metric("Totale Incassato", f"{df_vendite['totale'].sum()} €")
            st.subheader("Storico Ultime Operazioni")
            st.dataframe(df_vendite.sort_values(by='data', ascending=False), use_container_width=True)
        else:
            st.warning("Ancora nessuna vendita registrata.")

    if st.sidebar.button("Esci (Logout)"):
        st.session_state.autenticato = False
        st.rerun()
