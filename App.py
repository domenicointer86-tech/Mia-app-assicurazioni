import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIGURAZIONE DATABASE ---
conn = sqlite3.connect('ristopro_v7.db', check_same_thread=False)
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
        # Mostriamo anche la quantità nel PDF se presente
        qta_testo = f"x{p['qta']}" if 'qta' in p else ""
        pdf.cell(150, 10, txt=f"{nome} {qta_testo}", border=1)
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

# --- 4. LOGICA DI ACCESSO ---
if not st.session_state.autenticato:
    st.title("🔐 RistoPro v7.0 - Accesso")
    pwd = st.text_input("Password", type="password")
    if st.button("Entra"):
        if pwd == "admin123":
            st.session_state.autenticato = True
            st.rerun()
        else:
            st.error("Password errata")
else:
    st.sidebar.title("🍽️ RistoPro v7.0")
    app_mode = st.sidebar.radio("Naviga:", ["Gestione Sala", "Gestione Menu", "Magazzino", "Dashboard Incassi"])

    # --- SEZIONE GESTIONE MENU ---
    if app_mode == "Gestione Menu":
        st.header("📋 Editor del Menu")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            with st.form("add_menu_form", clear_on_submit=True):
                n_nome = st.text_input("Nome Piatto/Bevanda")
                n_cat = st.selectbox("Categoria", ["Primi", "Secondi", "Drink", "Dessert", "Altro"])
                n_prezzo = st.number_input("Prezzo Unitario (€)", min_value=0.0, step=0.5)
                if st.form_submit_button("Salva nel Menu"):
                    c.execute("INSERT OR REPLACE INTO menu (nome, categoria, prezzo) VALUES (?, ?, ?)", (n_nome, n_cat, n_prezzo))
                    conn.commit()
                    st.success("Salvato!")
        with col_m2:
            df_m = pd.read_sql_query("SELECT * FROM menu", conn)
            st.dataframe(df_m, use_container_width=True)

    # --- SEZIONE GESTIONE SALA (CON QUANTITÀ) ---
    elif app_mode == "Gestione Sala":
        st.header("📍 Gestione Ordini")
        df_menu_db = pd.read_sql_query("SELECT * FROM menu", conn)
        
        if df_menu_db.empty:
            st.warning("Aggiungi prodotti nel Menu prima di ordinare!")
        else:
            col_ord, col_conto = st.columns(2)
            
            with col_ord:
                st.subheader("📝 Nuovo Ordine")
                t_sel = st.selectbox("Tavolo", list(st.session_state.tavoli.keys()))
                cat_sel = st.selectbox("Categoria", df_menu_db['categoria'].unique())
                piatti_f = df_menu_db[df_menu_db['categoria'] == cat_sel]
                p_sel = st.selectbox("Prodotto", piatti_f['nome'].tolist())
                
                # AGGIUNTA CAMPO QUANTITÀ
                qta_sel = st.number_input("Quantità", min_value=1, max_value=50, value=1)
                
                prezzo_un = piatti_f[piatti_f['nome'] == p_sel]['prezzo'].values[0]
                prezzo_tot_riga = prezzo_un * qta_sel

                if st.button(f"Invia {qta_sel} {p_sel} in Cucina 🚀"):
                    c.execute("SELECT quantita FROM magazzino WHERE prodotto = ?", (p_sel,))
                    res = c.fetchone()
                    
                    if res and res[0] < qta_sel:
                        st.error(f"❌ Scorte insufficienti! Disponibili solo {res[0]} unità.")
                    else:
                        # Aggiungiamo l'ordine (moltiplicato per qta o come singola voce con qta indicata)
                        st.session_state.tavoli[t_sel].append({
                            "nome": p_sel, 
                            "qta": qta_sel, 
                            "prezzo": prezzo_tot_riga
                        })
                        if res:
                            c.execute("UPDATE magazzino SET quantita = quantita - ? WHERE prodotto = ?", (qta_sel, p_sel))
                        conn.commit()
                        st.success(f"Aggiunte {qta_sel} unità di {p_sel}")

            with col_conto:
                st.subheader(f"💰 Conto {t_sel}")
                if st.session_state.tavoli[t_sel]:
                    df_t = pd.DataFrame(st.session_state.tavoli[t_sel])
                    st.table(df_t)
                    totale = df_t['prezzo'].sum()
                    st.write(f"### Totale: {totale}€")
                    
                    pdf_b = crea_pdf(t_sel, st.session_state.tavoli[t_sel], totale)
                    st.download_button("🖨️ Scarica PDF", data=pdf_b, file_name=f"conto_{t_sel}.pdf")
                    
                    if st.button("Chiudi e Libera"):
                        p_nomi = ", ".join([f"{p['nome']}(x{p['qta']})" for p in st.session_state.tavoli[t_sel]])
                        c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                                  (t_sel, p_nomi, totale, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        conn.commit()
                        st.session_state.tavoli[t_sel] = []
                        st.rerun()

    # --- SEZIONE MAGAZZINO & DASHBOARD ---
    elif app_mode == "Magazzino":
        st.header("📦 Magazzino")
        df_mag = pd.read_sql_query("SELECT * FROM magazzino", conn)
        st.dataframe(df_mag)
        with st.form("m"):
            df_m_list = pd.read_sql_query("SELECT nome FROM menu", conn)
            p_m = st.selectbox("Prodotto", df_m_list['nome'].tolist()) if not df_m_list.empty else st.text_input("Nome")
            q_m = st.number_input("Aggiungi quantità", min_value=1)
            if st.form_submit_button("Carica"):
                c.execute("INSERT OR REPLACE INTO magazzino (prodotto, quantita) VALUES (?, COALESCE((SELECT quantita FROM magazzino WHERE prodotto = ?), 0) + ?)", (p_m, p_m, q_m))
                conn.commit()
                st.rerun()

    elif app_mode == "Dashboard Incassi":
        st.header("📊 Analisi")
        df_v = pd.read_sql_query("SELECT * FROM vendite", conn)
        if not df_v.empty:
            st.metric("Totale Incassato", f"{df_v['totale'].sum()} €")
            st.dataframe(df_v)

    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()
