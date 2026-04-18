import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- 1. DATABASE ---
conn = sqlite3.connect('ristopro_v12.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS vendite (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS magazzino (prodotto TEXT PRIMARY KEY, quantita INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS menu (nome TEXT PRIMARY KEY, categoria TEXT, prezzo REAL)')
conn.commit()

# --- 2. FUNZIONI ---
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
if 'tavoli' not in st.session_state: st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}
if 'vista_tavolo' not in st.session_state: st.session_state.vista_tavolo = None # Gestisce la schermata a parte

# --- 4. ACCESSO ---
if not st.session_state.autenticato:
    st.title("🔐 RistoPro v12.0")
    if st.text_input("Password", type="password") == "admin123":
        if st.button("Accedi"):
            st.session_state.autenticato = True
            st.rerun()
else:
    # Sidebar fissa
    st.sidebar.title("🚀 RistoPro")
    mode = st.sidebar.radio("Naviga:", ["Gestione Sala", "Magazzino", "Menu", "Statistiche"])

    # --- SCHERMATA GESTIONE SALA ---
    if mode == "Gestione Sala":
        
        # LOGICA: Mostra la Mappa o la Schermata del Tavolo?
        if st.session_state.vista_tavolo is None:
            st.header("📍 Seleziona un Tavolo")
            # Griglia 4x3
            t_lista = list(st.session_state.tavoli.keys())
            for i in range(0, len(t_lista), 4):
                cols = st.columns(4)
                for j, col in enumerate(cols):
                    if i + j < len(t_lista):
                        tn = t_lista[i + j]
                        occ = len(st.session_state.tavoli[tn]) > 0
                        icona = "🔴" if occ else "🟢"
                        if col.button(f"{icona}\n{tn}", key=tn, use_container_width=True):
                            st.session_state.vista_tavolo = tn
                            st.rerun()
        
        else:
            # --- SCHERMATA A PARTE DEL TAVOLO ---
            t_corrente = st.session_state.vista_tavolo
            st.header(f"🛒 Ordine: {t_corrente}")
            
            # Tasto per tornare indietro alla sala
            if st.button("⬅️ Torna alla Mappa Sala"):
                st.session_state.vista_tavolo = None
                st.rerun()

            st.divider()
            
            df_menu = pd.read_sql_query("SELECT * FROM menu", conn)
            if df_menu.empty:
                st.warning("Il menu è vuoto! Aggiungi prodotti nella sezione Menu.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Aggiungi Merce")
                    prod = st.selectbox("Prodotto", df_menu['nome'].tolist())
                    qta = st.number_input("Quantità", min_value=1, value=1)
                    if st.button("Conferma e Aggiungi ✅"):
                        c.execute("SELECT quantita FROM magazzino WHERE prodotto = ?", (prod,))
                        res = c.fetchone()
                        if res and res[0] >= qta:
                            prezzo_u = df_menu[df_menu['nome'] == prod]['prezzo'].values[0]
                            st.session_state.tavoli[t_corrente].append({"nome": prod, "qta": qta, "prezzo": round(prezzo_u * qta, 2)})
                            c.execute("UPDATE magazzino SET quantita = quantita - ? WHERE prodotto = ?", (qta, prod))
                            conn.commit()
                            st.success("Aggiunto!")
                            st.rerun()
                        else:
                            st.error("Scorte insufficienti!")

                with c2:
                    st.subheader("Conto Attuale")
                    if st.session_state.tavoli[t_corrente]:
                        df_res = pd.DataFrame(st.session_state.tavoli[t_corrente])
                        st.table(df_res)
                        tot = round(df_res['prezzo'].sum(), 2)
                        st.write(f"## Totale: {tot} €")
                        
                        pdf_data = crea_pdf(t_corrente, st.session_state.tavoli[t_corrente], tot)
                        st.download_button("🖨️ Stampa Scontrino", data=pdf_data, file_name=f"{t_corrente}.pdf")
                        
                        if st.button("💰 PAGATO (Libera e Torna alla Sala)"):
                            # Salva vendita
                            lista_p = ", ".join([f"{x['nome']}x{x['qta']}" for x in st.session_state.tavoli[t_corrente]])
                            c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                                      (t_corrente, lista_p, tot, datetime.now().strftime("%Y-%m-%d %H:%M")))
                            conn.commit()
                            # Svuota e torna indietro
                            st.session_state.tavoli[t_corrente] = []
                            st.session_state.vista_tavolo = None
                            st.success("Incasso registrato!")
                            st.rerun()
                    else:
                        st.info("Nessun ordine per questo tavolo.")

    # --- ALTRE SEZIONI ---
    elif mode == "Magazzino":
        st.header("📦 Magazzino")
        st.dataframe(pd.read_sql_query("SELECT * FROM magazzino", conn), use_container_width=True)
        with st.form("c"):
            p = st.text_input("Prodotto")
            q = st.number_input("Q.tà", min_value=1)
            if st.form_submit_button("Carica"):
                c.execute("INSERT OR REPLACE INTO magazzino (prodotto, quantita) VALUES (?, COALESCE((SELECT quantita FROM magazzino WHERE prodotto = ?), 0) + ?)", (p, p, q))
                conn.commit()
