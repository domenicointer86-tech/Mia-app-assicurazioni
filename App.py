import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIGURAZIONE DATABASE ---
# Il file .db salva fisicamente i tuoi dati su disco/cloud
conn = sqlite3.connect('ristopro_v9.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vendite 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS magazzino 
             (prodotto TEXT PRIMARY KEY, quantita INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS menu 
             (nome TEXT PRIMARY KEY, categoria TEXT, prezzo REAL)''')
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
        pdf.cell(150, 10, txt=f"{nome} x{p['qta']}", border=1)
        pdf.cell(40, 10, txt=f"{p['prezzo']} Euro", border=1, ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"TOTALE: {totale} Euro", ln=True)
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- 3. INIZIALIZZAZIONE ---
if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 11)}

# --- 4. LOGIN ---
if not st.session_state.autenticato:
    st.title("🔐 RistoPro v9.0 - Login")
    pwd = st.text_input("Password", type="password")
    if st.button("Entra"):
        if pwd == "admin123":
            st.session_state.autenticato = True
            st.rerun()
else:
    st.sidebar.title("🍽️ Gestionale Pro")
    app_mode = st.sidebar.radio("Menu:", ["Gestione Sala", "Gestione Menu", "Magazzino", "Dashboard Incassi"])

    # --- SEZIONE MENU ---
    if app_mode == "Gestione Menu":
        st.header("📋 Imposta il tuo Menu")
        with st.form("menu_form"):
            n = st.text_input("Nome Prodotto")
            c_cat = st.selectbox("Categoria", ["Drink", "Primi", "Secondi", "Pizze", "Altro"])
            p = st.number_input("Prezzo (€)", min_value=0.0, step=0.1)
            if st.form_submit_button("Salva nel Menu"):
                c.execute("INSERT OR REPLACE INTO menu VALUES (?, ?, ?)", (n, c_cat, p))
                conn.commit()
                st.success("Prodotto salvato!")
        
        df_m = pd.read_sql_query("SELECT * FROM menu", conn)
        st.dataframe(df_m, use_container_width=True)

    # --- SEZIONE SALA ---
    elif app_mode == "Gestione Sala":
        st.header("📍 Sala e Comande")
        df_menu_db = pd.read_sql_query("SELECT * FROM menu", conn)
        if df_menu_db.empty:
            st.warning("Carica prima il Menu!")
        else:
            t_sel = st.selectbox("Tavolo", list(st.session_state.tavoli.keys()))
            col1, col2 = st.columns(2)
            
            with col1:
                p_sel = st.selectbox("Cosa desiderano?", df_menu_db['nome'].tolist())
                q_sel = st.number_input("Quantità", min_value=1, value=1)
                if st.button("Invia Ordine 🚀"):
                    c.execute("SELECT quantita FROM magazzino WHERE prodotto = ?", (p_sel,))
                    res = c.fetchone()
                    if res and res[0] >= q_sel:
                        prezzo_un = df_menu_db[df_menu_db['nome'] == p_sel]['prezzo'].values[0]
                        st.session_state.tavoli[t_sel].append({"nome": p_sel, "qta": q_sel, "prezzo": prezzo_un * q_sel})
                        c.execute("UPDATE magazzino SET quantita = quantita - ? WHERE prodotto = ?", (q_sel, p_sel))
                        conn.commit()
                        st.rerun()
                    else:
                        st.error("Scorte insufficienti in Magazzino!")

            with col2:
                if st.session_state.tavoli[t_sel]:
                    df_t = pd.DataFrame(st.session_state.tavoli[t_sel])
                    st.table(df_t)
                    tot = round(df_t['prezzo'].sum(), 2)
                    st.write(f"### Totale: {tot}€")
                    if st.button("Chiudi e Salva Incasso"):
                        p_str = ", ".join([f"{x['nome']}x{x['qta']}" for x in st.session_state.tavoli[t_sel]])
                        c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                                  (t_sel, p_str, tot, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        conn.commit()
                        st.session_state.tavoli[t_sel] = []
                        st.rerun()

    # --- SEZIONE MAGAZZINO (SALVATAGGIO PERSISTENTE) ---
    elif app_mode == "Magazzino":
        st.header("📦 Gestione Magazzino Persistente")
        
        # 1. Visualizzazione Scorte
        df_mag = pd.read_sql_query("SELECT * FROM magazzino", conn)
        st.subheader("Giacenza Attuale")
        st.dataframe(df_mag, use_container_width=True)

        st.divider()

        # 2. Carico Merce
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("📥 Carica Merce")
            with st.form("carico_merce"):
                # Suggerisce i nomi dai prodotti a Menu
                df_menu_nomi = pd.read_sql_query("SELECT nome FROM menu", conn)
                prod_carico = st.selectbox("Scegli Prodotto", df_menu_nomi['nome'].tolist()) if not df_menu_nomi.empty else st.text_input("Nome Prodotto")
                qta_carico = st.number_input("Quantità da aggiungere", min_value=1)
                if st.form_submit_button("Conferma Carico"):
                    # COALESCE gestisce il caso in cui il prodotto non sia mai stato caricato prima
                    c.execute('''INSERT OR REPLACE INTO magazzino (prodotto, quantita) 
                                 VALUES (?, COALESCE((SELECT quantita FROM magazzino WHERE prodotto = ?), 0) + ?)''', 
                              (prod_carico, prod_carico, qta_carico))
                    conn.commit()
                    st.success(f"Caricamento di {prod_carico} salvato!")
                    st.rerun()

        with col_c2:
            st.subheader("🔧 Rettifica Inventario")
            with st.form("rettifica_merce"):
                prod_mod = st.selectbox("Prodotto da modificare", df_mag['prodotto'].tolist()) if not df_mag.empty else st.text_input("Nome")
                nuova_qta = st.number_input("Imposta Nuova Quantità Esatta", min_value=0)
                if st.form_submit_button("Sovrascrivi Quantità"):
                    c.execute("UPDATE magazzino SET quantita = ? WHERE prodotto = ?", (nuova_qta, prod_mod))
                    conn.commit()
                    st.warning(f"Quantità di {prod_mod} aggiornata a {nuova_qta}")
                    st.rerun()

    # --- SEZIONE DASHBOARD ---
    elif app_mode == "Dashboard Incassi":
        st.header("📊 Analisi Incassi")
        df_v = pd.read_sql_query("SELECT * FROM vendite", conn)
        if not df_v.empty:
            df_v['data'] = pd.to_datetime(df_v['data'])
            df_v['giorno'] = df_v['data'].dt.date
            inc_giorn = df_v.groupby('giorno')['totale'].sum()
            st.line_chart(inc_giorn)
            st.table(inc_giorn)
        else:
            st.info("Dati non ancora disponibili.")

    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()
