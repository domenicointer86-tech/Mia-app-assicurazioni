import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIGURAZIONE DATABASE ---
conn = sqlite3.connect('ristopro_finale.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vendite 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS magazzino 
             (prodotto TEXT PRIMARY KEY, quantita INTEGER)''')
# Nuova tabella per il Menù personalizzabile
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

# --- 4. LOGICA DI ACCESSO ---
if not st.session_state.autenticato:
    st.title("🔐 RistoPro - Accesso Professionale")
    pwd = st.text_input("Password", type="password")
    if st.button("Entra"):
        if pwd == "admin123":
            st.session_state.autenticato = True
            st.rerun()
        else:
            st.error("Password errata")
else:
    # --- 5. INTERFACCIA PRINCIPALE ---
    st.sidebar.title("🍽️ RistoPro v6.0")
    app_mode = st.sidebar.radio("Naviga:", ["Gestione Sala", "Gestione Menu", "Magazzino", "Dashboard Incassi"])

    # --- SEZIONE GESTIONE MENU (NUOVA) ---
    if app_mode == "Gestione Menu":
        st.header("📋 Editor del Menu")
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.subheader("Aggiungi Prodotto")
            with st.form("add_menu_form", clear_on_submit=True):
                nuovo_nome = st.text_input("Nome Piatto/Bevanda")
                nuova_cat = st.selectbox("Categoria", ["Primi", "Secondi", "Pizze", "Drink", "Dessert", "Altro"])
                nuovo_prezzo = st.number_input("Prezzo (€)", min_value=0.0, step=0.5)
                if st.form_submit_button("Salva nel Menu"):
                    if nuovo_nome:
                        c.execute("INSERT OR REPLACE INTO menu (nome, categoria, prezzo) VALUES (?, ?, ?)", 
                                  (nuovo_nome, nuova_cat, nuovo_prezzo))
                        conn.commit()
                        st.success(f"{nuovo_nome} salvato con successo!")
                    else:
                        st.error("Inserisci un nome!")

        with col_m2:
            st.subheader("Menu Attuale")
            df_menu = pd.read_sql_query("SELECT * FROM menu", conn)
            st.dataframe(df_menu, use_container_width=True)
            if st.button("Svuota tutto il Menu"):
                c.execute("DELETE FROM menu")
                conn.commit()
                st.rerun()

    # --- SEZIONE GESTIONE SALA (MODIFICATA) ---
    elif app_mode == "Gestione Sala":
        st.header("📍 Mappa Tavoli")
        df_menu_db = pd.read_sql_query("SELECT * FROM menu", conn)
        
        if df_menu_db.empty:
            st.warning("⚠️ Il menu è vuoto! Vai nella sezione 'Gestione Menu' per aggiungere i tuoi prodotti.")
        else:
            col_ord, col_conto = st.columns(2)
            
            with col_ord:
                st.subheader("📝 Nuovo Ordine")
                t_sel = st.selectbox("Seleziona Tavolo", list(st.session_state.tavoli.keys()))
                
                # Filtro categorie dinamico dal DB
                categorie_disp = df_menu_db['categoria'].unique()
                cat_sel = st.selectbox("Seleziona Categoria", categorie_disp)
                
                # Filtro piatti basato sulla categoria
                piatti_filtrati = df_menu_db[df_menu_db['categoria'] == cat_sel]
                piatto_sel = st.selectbox("Seleziona Piatto", piatti_filtrati['nome'].tolist())
                prezzo_sel = piatti_filtrati[piatti_filtrati['nome'] == piatto_sel]['prezzo'].values[0]

                if st.button("Invia in Cucina 🚀"):
                    c.execute("SELECT quantita FROM magazzino WHERE prodotto = ?", (piatto_sel,))
                    res = c.fetchone()
                    
                    # Se il prodotto non è in magazzino, lo trattiamo come illimitato o diamo errore?
                    # Qui lo trattiamo come controllo magazzino se esiste:
                    if res and res[0] <= 0:
                        st.error(f"❌ {piatto_sel} ESAURITO in Magazzino!")
                    else:
                        st.session_state.tavoli[t_sel].append({"nome": piatto_sel, "prezzo": prezzo_sel})
                        if res:
                            c.execute("UPDATE magazzino SET quantita = quantita - 1 WHERE prodotto = ?", (piatto_sel,))
                        conn.commit()
                        st.success(f"Aggiunto {piatto_sel} ({prezzo_sel}€)")

            with col_conto:
                st.subheader(f"💰 Conto {t_sel}")
                if st.session_state.tavoli[t_sel]:
                    df_tavolo = pd.DataFrame(st.session_state.tavoli[t_sel])
                    st.table(df_tavolo)
                    totale = df_tavolo['prezzo'].sum()
                    st.write(f"### Totale: {totale}€")
                    
                    pdf_bytes = crea_pdf(t_sel, st.session_state.tavoli[t_sel], totale)
                    st.download_button("🖨️ Scarica PDF", data=pdf_bytes, file_name=f"conto_{t_sel}.pdf")
                    
                    if st.button("Paga e Libera"):
                        nomi_piatti = ", ".join([p['nome'] for p in st.session_state.tavoli[t_sel]])
                        c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                                  (t_sel, nomi_piatti, totale, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        conn.commit()
                        st.session_state.tavoli[t_sel] = []
                        st.rerun()

    # --- SEZIONE MAGAZZINO ---
    elif app_mode == "Magazzino":
        st.header("📦 Magazzino Scorte")
        df_mag = pd.read_sql_query("SELECT * FROM magazzino", conn)
        st.bar_chart(df_mag.set_index('prodotto')['quantita'])
        
        with st.form("mag_form"):
            # Carica suggerimenti dal menu per il magazzino
            df_m = pd.read_sql_query("SELECT nome FROM menu", conn)
            p_nome = st.selectbox("Scegli prodotto dal Menu", df_m['nome'].tolist()) if not df_m.empty else st.text_input("Nome Prodotto")
            p_qta = st.number_input("Quantità da aggiungere", min_value=1)
            if st.form_submit_button("Aggiorna Scorte"):
                c.execute("INSERT OR REPLACE INTO magazzino (prodotto, quantita) VALUES (?, COALESCE((SELECT quantita FROM magazzino WHERE prodotto = ?), 0) + ?)", (p_nome, p_nome, p_qta))
                conn.commit()
                st.rerun()

    # --- SEZIONE DASHBOARD ---
    elif app_mode == "Dashboard Incassi":
        st.header("📊 Analisi Vendite")
        df_v = pd.read_sql_query("SELECT * FROM vendite", conn)
        if not df_v.empty:
            st.metric("Incasso Totale", f"{df_v['totale'].sum()} €")
            st.write("Ultimi ordini chiusi:")
            st.dataframe(df_v)
        else:
            st.info("Nessun dato.")

    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()
