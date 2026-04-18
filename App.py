import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIGURAZIONE DATABASE ---
conn = sqlite3.connect('ristopro_v5.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vendite 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS magazzino 
             (prodotto TEXT PRIMARY KEY, quantita INTEGER)''')
conn.commit()

# --- 2. FUNZIONI DI SERVIZIO ---
def crea_pdf(tavolo, piatti, totale):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"RICEVUTA - {tavolo}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(10)
    for p in piatti:
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
    "Primi": {"Carbonara": 12.0, "Lasagna": 10.0},
    "Secondi": {"Tagliata": 18.0, "Orata": 15.0},
    "Drink": {"Birra": 5.0, "Vino": 4.0, "Acqua": 2.0}
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
    st.sidebar.title("🍽️ RistoPro v5.0")
    app_mode = st.sidebar.radio("Vai a:", ["Gestione Sala", "Magazzino", "Dashboard Incassi"])

    if app_mode == "Gestione Sala":
        st.header("📍 Mappa Tavoli")
        
        # Alert scorte basse
        df_low = pd.read_sql_query("SELECT * FROM magazzino WHERE quantita < 5", conn)
        if not df_low.empty:
            st.warning(f"⚠️ Scorte basse per: {', '.join(df_low['prodotto'].tolist())}")

        col_ord, col_conto = st.columns(2)
        
        with col_ord:
            st.subheader("📝 Nuovo Ordine")
            t_sel = st.selectbox("Seleziona Tavolo", list(st.session_state.tavoli.keys()))
            cat_sel = st.selectbox("Categoria", list(menu_ristorante.keys()))
            piatto_sel = st.selectbox("Piatto", list(menu_ristorante[cat_sel].keys()))
            
            if st.button("Invia in Cucina 🚀"):
                c.execute("SELECT quantita FROM magazzino WHERE prodotto = ?", (piatto_sel,))
                res = c.fetchone()
                if res and res[0] > 0:
                    st.session_state.tavoli[t_sel].append({"nome": piatto_sel, "prezzo": menu_ristorante[cat_sel][piatto_sel]})
                    c.execute("UPDATE magazzino SET quantita = quantita - 1 WHERE prodotto = ?", (piatto_sel,))
                    conn.commit()
                    st.success(f"{piatto_sel} aggiunto! Rimanenti: {res[0]-1}")
                else:
                    st.error(f"❌ {piatto_sel} ESAURITO o non caricato in Magazzino!")

        with col_conto:
            st.subheader(f"💰 Conto {t_sel}")
            if st.session_state.tavoli[t_sel]:
                df = pd.DataFrame(st.session_state.tavoli[t_sel])
                st.table(df)
                totale = df['prezzo'].sum()
                pdf_bytes = crea_pdf(t_sel, st.session_state.tavoli[t_sel], totale)
                st.download_button("🖨️ Stampa Scontrino", data=pdf_bytes, file_name=f"conto_{t_sel}.pdf")
                if st.button("Paga e Libera"):
                    piatti_str = ", ".join([p['nome'] for p in st.session_state.tavoli[t_sel]])
                    c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                              (t_sel, piatti_str, totale, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    st.session_state.tavoli[t_sel] = []
                    st.rerun()

    elif app_mode == "Magazzino":
        st.header("📦 Gestione Scorte & Analytics")
        df_mag = pd.read_sql_query("SELECT * FROM magazzino", conn)
        
        if not df_mag.empty:
            st.bar_chart(df_mag.set_index('prodotto')['quantita'])
        
        st.subheader("➕ Carica / Aggiorna Prodotti")
        with st.form("mag_form"):
            p_nome = st.text_input("Nome Prodotto (esatto)")
            p_qta = st.number_input("Quantità", min_value=1, value=10)
            if st.form_submit_button("Aggiorna Inventario"):
                c.execute("INSERT OR REPLACE INTO magazzino (prodotto, quantita) VALUES (?, COALESCE((SELECT quantita FROM magazzino WHERE prodotto = ?), 0) + ?)", (p_nome, p_nome, p_qta))
                conn.commit()
                st.rerun()

    elif app_mode == "Dashboard Incassi":
        st.header("📊 Analisi Performance")
        df_v = pd.read_sql_query("SELECT * FROM vendite", conn)
        if not df_v.empty:
            st.metric("Incasso Totale", f"{df_v['totale'].sum()} €")
            # Grafico dei piatti più venduti
            tutti_p = []
            for s in df_v['piatti']: tutti_p.extend(s.split(", "))
            st.subheader("Piatti più venduti")
            st.bar_chart(pd.Series(tutti_p).value_counts())
        else:
            st.info("Nessuna vendita.")

    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()
