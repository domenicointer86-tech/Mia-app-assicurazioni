import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF
import base64

# --- CONFIGURAZIONE DATABASE ---
conn = sqlite3.connect('gestionale_v3.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS ordini_chiusi 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)''')
conn.commit()

# --- LOGICA PDF ---
def crea_pdf(tavolo, piatti, totale):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"RICEVUTA - {tavolo}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(10)
    
    for p in piatti:
        pdf.cell(150, 10, txt=f"{p['nome']}", border=1)
        pdf.cell(40, 10, txt=f"{p['prezzo']}€", border=1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"TOTALE DA PAGARE: {totale}€", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACCIA ---
st.set_page_config(page_title="RistoPro 2026", layout="wide")

# Login Semplice
if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Accesso Gestionale")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("Entra"):
        if pwd == "admin123": # Cambiala con una seria!
            st.session_state.autenticato = True
            st.rerun()
else:
    # --- APP REALE ---
    st.sidebar.title("🚀 RistoPro v3.0")
    menu_app = st.sidebar.radio("Naviga", ["Sala e Ordini", "Cucina", "Magazzino e Statistiche"])

    # Dati in memoria per i tavoli aperti
    if 'tavoli_attivi' not in st.session_state:
        st.session_state.tavoli_attivi = {f"Tavolo {i}": [] for i in range(1, 11)}

    menu_ristorante = {
        "Primi": {"Carbonara": 12.0, "Lasagna": 10.0},
        "Secondi": {"Tagliata": 18.0, "Orata": 15.0},
        "Drink": {"Spritz": 6.0, "Birra 0.4": 5.0, "Acqua": 2.0}
    }

    if menu_app == "Sala e Ordini":
        st.header("📍 Gestione Sala")
        col1, col2 = st.columns([1, 2])

        with col1:
            t_sel = st.selectbox("Seleziona Tavolo", list(st.session_state.tavoli_attivi.keys()))
            cat_sel = st.selectbox("Categoria", list(menu_ristorante.keys()))
            piatto_sel = st.selectbox("Piatto", list(menu_ristorante[cat_sel].keys()))
            
            if st.button("Invia in Cucina"):
                st.session_state.tavoli_attivi[t_sel].append({
                    "nome": piatto_sel, "prezzo": menu_ristorante[cat_sel][piatto_sel]
                })
                st.toast(f"Inviato: {piatto_sel}")

        with col2:
            st.subheader(f"Dettaglio {t_sel}")
            if st.session_state.tavoli_attivi[t_sel]:
                df_tavolo = pd.DataFrame(st.session_state.tavoli_attivi[t_sel])
                st.table(df_tavolo)
                totale = df_tavolo['prezzo'].sum()
                st.write(f"### Totale: {totale}€")

                # Generazione PDF e Chiusura
                pdf_data = crea_pdf(t_sel, st.session_state.tavoli_attivi[t_sel], totale)
                st.download_button("🖨️ Scarica Pre-conto PDF", data=pdf_data, file_name=f"conto_{t_sel}.pdf")

                if st.button("✅ Pagato e Chiudi"):
                    # Salva nel DB
                    lista_nomi = ", ".join([p['nome'] for p in st.session_state.tavoli_attivi[t_sel]])
                    c.execute("INSERT INTO ordini_chiusi (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                              (t_sel, lista_nomi, totale, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    st.session_state.tavoli_attivi[t_sel] = []
                    st.success("Conto chiuso e salvato!")
                    st.rerun()
            else:
                st.info("Tavolo libero")

    elif menu_app == "Magazzino e Statistiche":
        st.header("📈 Analisi Business")
        df_storia = pd.read_sql_query("SELECT * FROM ordini_chiusi", conn)
        if not df_storia.empty:
            st.metric("Incasso Totale Periodo", f"{df_storia['totale'].sum()} €")
            st.line_chart(df_storia.set_index('data')['totale'])
            st.dataframe(df_storia)
        else:
            st.write("Nessun dato ancora disponibile.")

    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()
