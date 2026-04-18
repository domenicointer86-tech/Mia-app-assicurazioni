import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- 1. DATABASE ---
conn = sqlite3.connect('ristopro_v10.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS vendite (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS magazzino (prodotto TEXT PRIMARY KEY, quantita INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS menu (nome TEXT PRIMARY KEY, categoria TEXT, prezzo REAL)')
conn.commit()

# --- 2. PDF ---
def crea_pdf(tavolo, piatti, totale):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"RICEVUTA - {tavolo}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for p in piatti:
        nome = p['nome'].replace('à','a').replace('è','e').replace('é','e').replace('ì','i').replace('ò','o').replace('ù','u')
        pdf.cell(150, 10, txt=f"{nome} x{p['qta']}", border=1)
        pdf.cell(40, 10, txt=f"{p['prezzo']} Euro", border=1, ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"TOTALE: {totale} Euro", ln=True)
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- 3. SESSION STATE ---
if 'autenticato' not in st.session_state: st.session_state.autenticato = False
if 'tavoli' not in st.session_state: st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)} # 12 Tavoli
if 'tavolo_selezionato' not in st.session_state: st.session_state.tavolo_selezionato = None

# --- 4. LOGIN ---
if not st.session_state.autenticato:
    st.title("🔐 RistoPro v10.0")
    if st.text_input("Password", type="password") == "admin123":
        if st.button("Entra"): 
            st.session_state.autenticato = True
            st.rerun()
else:
    st.sidebar.title("🍽️ Gestionale")
    app_mode = st.sidebar.radio("Menu:", ["Gestione Sala", "Gestione Menu", "Magazzino", "Dashboard Incassi"])

    # --- GESTIONE MENU ---
    if app_mode == "Gestione Menu":
        st.header("📋 Imposta Menu")
        with st.form("m_form"):
            n = st.text_input("Nome")
            p = st.number_input("Prezzo", min_value=0.0, step=0.1)
            cat = st.selectbox("Categoria", ["Drink", "Cibo", "Altro"])
            if st.form_submit_button("Salva"):
                c.execute("INSERT OR REPLACE INTO menu VALUES (?, ?, ?)", (n, cat, p))
                conn.commit()
        st.dataframe(pd.read_sql_query("SELECT * FROM menu", conn), use_container_width=True)

    # --- GESTIONE SALA (MAPPA TAVOLI) ---
    elif app_mode == "Gestione Sala":
        st.header("📍 Mappa Sala")
        
        # Creazione dei tasti dei tavoli in fila (3 righe da 4 tavoli)
        tavoli_nomi = list(st.session_state.tavoli.keys())
        for riga in range(0, len(tavoli_nomi), 4):
            cols = st.columns(4)
            for i, col in enumerate(cols):
                if riga + i < len(tavoli_nomi):
                    nome_t = tavoli_nomi[riga + i]
                    # Cambia colore se occupato (usa icone come trucco visuale)
                    status = "🔴" if st.session_state.tavoli[nome_t] else "🟢"
                    if col.button(f"{status}\n{nome_t}", key=nome_t, use_container_width=True):
                        st.session_state.tavolo_selezionato = nome_t

        st.divider()

        # Se un tavolo è selezionato, mostra la gestione ordini
        if st.session_state.tavolo_selezionato:
            t_sel = st.session_state.tavolo_selezionato
            st.subheader(f"🛠️ Gestione {t_sel}")
            
            df_menu = pd.read_sql_query("SELECT * FROM menu", conn)
            if df_menu.empty:
                st.error("Il menu è vuoto!")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.write("### Aggiungi Merce")
                    p_nome = st.selectbox("Cosa hanno preso?", df_menu['nome'].tolist())
                    qta = st.number_input("Quanti?", min_value=1, value=1)
                    if st.button("Conferma Inserimento 🚀"):
                        # Controllo Magazzino
                        c.execute("SELECT quantita FROM magazzino WHERE prodotto = ?", (p_nome,))
                        res = c.fetchone()
                        if res and res[0] >= qta:
                            prezzo_un = df_menu[df_menu['nome'] == p_nome]['prezzo'].values[0]
                            st.session_state.tavoli[t_sel].append({"nome": p_nome, "qta": qta, "prezzo": prezzo_un * qta})
                            c.execute("UPDATE magazzino SET quantita = quantita - ? WHERE prodotto = ?", (qta, p_nome))
                            conn.commit()
                            st.success(f"Aggiunto {p_nome}!")
                            st.rerun()
                        else:
                            st.error("Scorte insufficienti!")

                with c2:
                    st.write("### Riepilogo Tavolo")
                    if st.session_state.tavoli[t_sel]:
                        df_t = pd.DataFrame(st.session_state.tavoli[t_sel])
                        st.table(df_t)
                        tot = round(df_t['prezzo'].sum(), 2)
                        st.write(f"**TOTALE: {tot} €**")
                        
                        pdf_b = crea_pdf(t_sel, st.session_state.tavoli[t_sel], tot)
                        st.download_button("🖨️ Scontrino PDF", data=pdf_b, file_name=f"{t_sel}.pdf")
                        
                        if st.button("PAGATO - Libera Tavolo"):
                            p_str = ", ".join([f"{x['nome']}x{x['qta']}" for x in st.session_state.tavoli[t_sel]])
                            c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                                      (t_sel, p_str, tot, datetime.now().strftime("%Y-%m-%d %H:%M")))
                            conn.commit()
                            st.session_state.tavoli[t_sel] = []
                            st.session_state.tavolo_selezionato = None
                            st.rerun()
                    else:
                        st.info("Il tavolo è vuoto.")

    # --- MAGAZZINO ---
    elif app_mode == "Magazzino":
        st.header("📦 Magazzino")
        df_mag = pd.read_sql_query("SELECT * FROM magazzino", conn)
        st.dataframe(df_mag, use_container_width=True)
        with st.form("carico"):
            p = st.text_input("Prodotto")
            q = st.number_input("Q.tà da aggiungere", min_value=1)
            if st.form_submit_button("Carica"):
                c.execute("INSERT OR REPLACE INTO magazzino (prodotto, quantita) VALUES (?, COALESCE((SELECT quantita FROM magazzino WHERE prodotto = ?), 0) + ?)", (p, p, q))
                conn.commit()
                st.rerun()

    # --- DASHBOARD ---
    elif app_mode == "Dashboard Incassi":
        st.header("📊 Incassi")
        df_v = pd.read_sql_query("SELECT * FROM vendite", conn)
        if not df_v.empty:
            st.metric("Totale Lordo", f"{round(df_v['totale'].sum(), 2)} €")
            st.dataframe(df_v)
        else: st.info("Nessun dato.")

    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()
