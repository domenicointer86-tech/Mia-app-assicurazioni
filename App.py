import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- 1. DATABASE (Salvataggio permanente) ---
conn = sqlite3.connect('ristopro_v14.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS vendite (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS menu (nome TEXT PRIMARY KEY, categoria TEXT, prezzo REAL)')
conn.commit()

# --- 2. FUNZIONE PDF ---
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
if 'vista_tavolo' not in st.session_state: st.session_state.vista_tavolo = None

# --- 4. ACCESSO ---
if not st.session_state.autenticato:
    st.title("🔐 RistoPro v14.0")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if pwd == "admin123":
            st.session_state.autenticato = True
            st.rerun()
else:
    st.sidebar.title("🚀 Menu Gestionale")
    mode = st.sidebar.radio("Scegli Sezione:", ["Gestione Sala", "Configura Menu", "Statistiche"])

    # --- SEZIONE CONFIGURA MENU (TUTTO SI SALVA QUI) ---
    if mode == "Configura Menu":
        st.header("📋 Archivio Prodotti e Prezzi")
        st.write("Inserisci qui la tua merce. Resterà salvata anche se chiudi l'app.")
        
        c1, c2 = st.columns([1, 1.5])
        with c1:
            with st.form("nuovo_prodotto", clear_on_submit=True):
                nome_p = st.text_input("Nome Merce (es. Birra, Caffè)")
                prezzo_p = st.number_input("Prezzo di vendita (€)", min_value=0.0, step=0.1)
                cat_p = st.selectbox("Categoria", ["Drink", "Cibo", "Servizi", "Altro"])
                if st.form_submit_button("💾 Salva nel Listino"):
                    if nome_p:
                        c.execute("INSERT OR REPLACE INTO menu (nome, categoria, prezzo) VALUES (?, ?, ?)", (nome_p, cat_p, prezzo_p))
                        conn.commit()
                        st.success(f"Salvo: {nome_p}")
                        st.rerun()

        with c2:
            df_m = pd.read_sql_query("SELECT * FROM menu ORDER BY nome", conn)
            st.write("**La tua merce salvata:**")
            st.dataframe(df_m, use_container_width=True, hide_index=True)
            
            p_da_canc = st.selectbox("Seleziona per eliminare", df_m['nome'].tolist() if not df_m.empty else [""])
            if st.button("🗑️ Elimina dal database"):
                c.execute("DELETE FROM menu WHERE nome = ?", (p_da_canc,))
                conn.commit()
                st.rerun()

    # --- SEZIONE GESTIONE SALA (MAPPA + SCHERMATA APERTA) ---
    elif mode == "Gestione Sala":
        if st.session_state.vista_tavolo is None:
            st.header("📍 Seleziona Tavolo")
            t_lista = list(st.session_state.tavoli.keys())
            for i in range(0, len(t_lista), 4):
                cols = st.columns(4)
                for j, col in enumerate(cols):
                    if i + j < len(t_lista):
                        tn = t_lista[i + j]
                        is_occ = len(st.session_state.tavoli[tn]) > 0
                        color = "🔴" if is_occ else "🟢"
                        if col.button(f"{color}\n{tn}", key=tn, use_container_width=True):
                            st.session_state.vista_tavolo = tn
                            st.rerun()
        else:
            # --- SCHERMATA INTERNA DEL TAVOLO ---
            t_sel = st.session_state.vista_tavolo
            st.header(f"🛒 Ordine {t_sel}")
            if st.button("⬅️ Torna alla Sala"):
                st.session_state.vista_tavolo = None
                st.rerun()

            st.divider()
            df_menu_db = pd.read_sql_query("SELECT * FROM menu", conn)
            
            if df_menu_db.empty:
                st.error("⚠️ Il tuo listino è vuoto. Vai in 'Configura Menu'!")
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.subheader("Aggiungi Merce")
                    p_scelto = st.selectbox("Scegli tra i prodotti salvati", df_menu_db['nome'].tolist())
                    q_scelta = st.number_input("Quantità", min_value=1, value=1)
                    if st.button("Inserisci nell'ordine"):
                        prezzo_unitario = df_menu_db[df_menu_db['nome'] == p_scelto]['prezzo'].values[0]
                        st.session_state.tavoli[t_sel].append({
                            "nome": p_scelto, 
                            "qta": q_scelta, 
                            "prezzo": round(prezzo_unitario * q_scelta, 2)
                        })
                        st.success(f"Aggiunto {p_scelto}")
                        st.rerun()

                with col_b:
                    st.subheader("Conto")
                    if st.session_state.tavoli[t_sel]:
                        df_ordine = pd.DataFrame(st.session_state.tavoli[t_sel])
                        st.table(df_ordine)
                        tot = round(df_ordine['prezzo'].sum(), 2)
                        st.write(f"### Totale: {tot} €")
                        
                        pdf_file = crea_pdf(t_sel, st.session_state.tavoli[t_sel], tot)
                        st.download_button("🖨️ Scarica Scontrino", data=pdf_file, file_name=f"{t_sel}.pdf")
                        
                        if st.button("💰 ORDINE PAGATO"):
                            # Registra la vendita nel database
                            p_string = ", ".join([f"{x['nome']}x{x['qta']}" for x in st.session_state.tavoli[t_sel]])
                            c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                                      (t_sel, p_string, tot, datetime.now().strftime("%Y-%m-%d %H:%M")))
                            conn.commit()
                            # Svuota e torna in sala
                            st.session_state.tavoli[t_sel] = []
                            st.session_state.vista_tavolo = None
                            st.rerun()
                    else:
                        st.info("Tavolo vuoto.")

    # --- STATISTICHE ---
    elif mode == "Statistiche":
        st.header("📊 Storico Vendite")
        df_v = pd.read_sql_query("SELECT * FROM vendite", conn)
        if not df_v.empty:
            st.metric("Incasso Totale", f"{round(df_v['totale'].sum(), 2)} €")
            st.dataframe(df_v, use_container_width=True)
        else:
            st.info("Nessuna vendita registrata.")

    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()
