import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from escpos.printer import Usb # Assicurati di aver fatto: pip install python-escpos

# --- CONFIGURAZIONE STAMPANTE (I TUOI DATI) ---
def esegui_stampa_termica(tavolo, piatti, totale):
    try:
        # Usiamo i codici VID e PID che hai trovato
        p = Usb(0x0DD4, 0x015F) 
        
        # Formattazione Scontrino
        p.set(align='center', text_type='B', width=2, height=2)
        p.text("RICEVUTA\n")
        p.set(align='center', text_type='NORMAL', width=1, height=1)
        p.text(f"{tavolo}\n")
        p.text(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        p.text("-" * 32 + "\n")
        
        p.set(align='left')
        for item in piatti:
            # Tronca il nome se troppo lungo per la carta da 58/80mm
            nome_pulito = item['nome'][:20]
            p.text(f"{nome_pulito} x{item['qta']} : {item['prezzo']}€\n")
            
        p.text("-" * 32 + "\n")
        p.set(align='right', text_type='B')
        p.text(f"TOTALE: {totale} Euro\n")
        p.ln(3)
        p.cut() # Comando di taglio automatico
        return True
    except Exception as e:
        st.error(f"⚠️ Errore Stampante: {e}")
        return False

# --- DATABASE ---
conn = sqlite3.connect('ristopro_v16.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS vendite (id INTEGER PRIMARY KEY AUTOINCREMENT, tavolo TEXT, piatti TEXT, totale REAL, data TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS menu (nome TEXT PRIMARY KEY, categoria TEXT, prezzo REAL)')
conn.commit()

# --- INTERFACCIA ---
if 'autenticato' not in st.session_state: st.session_state.autenticato = False
if 'tavoli' not in st.session_state: st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}
if 'vista_tavolo' not in st.session_state: st.session_state.vista_tavolo = None

if not st.session_state.autenticato:
    st.title("🔐 RistoPro v16.0 - Custom Edition")
    if st.text_input("Password", type="password") == "admin123":
        if st.button("Entra"): 
            st.session_state.autenticato = True
            st.rerun()
else:
    mode = st.sidebar.radio("Naviga:", ["Gestione Sala", "Configura Menu", "Statistiche"])

    if mode == "Configura Menu":
        st.header("📋 Archivio Prodotti")
        with st.form("add_menu"):
            n = st.text_input("Nome Prodotto")
            p = st.number_input("Prezzo (€)", min_value=0.0)
            if st.form_submit_button("Salva nel Menu"):
                c.execute("INSERT OR REPLACE INTO menu VALUES (?, 'Generale', ?)", (n, p))
                conn.commit()
                st.success("Salvato!")
                st.rerun()
        st.dataframe(pd.read_sql_query("SELECT * FROM menu", conn), use_container_width=True)

    elif mode == "Gestione Sala":
        if st.session_state.vista_tavolo is None:
            st.header("📍 Mappa Tavoli")
            cols = st.columns(4)
            for i, t_nome in enumerate(st.session_state.tavoli.keys()):
                with cols[i % 4]:
                    status = "🔴" if st.session_state.tavoli[t_nome] else "🟢"
                    if st.button(f"{status}\n{t_nome}", key=t_nome, use_container_width=True):
                        st.session_state.vista_tavolo = t_nome
                        st.rerun()
        else:
            t_sel = st.session_state.vista_tavolo
            st.header(f"🛒 Ordine {t_sel}")
            if st.button("⬅️ Torna alla Sala"):
                st.session_state.vista_tavolo = None
                st.rerun()
            
            df_m = pd.read_sql_query("SELECT * FROM menu", conn)
            if not df_m.empty:
                col1, col2 = st.columns(2)
                with col1:
                    prod = st.selectbox("Seleziona Prodotto", df_m['nome'].tolist())
                    qta = st.number_input("Quantità", min_value=1, value=1)
                    if st.button("Aggiungi all'Ordine ✅"):
                        prz = df_m[df_m['nome'] == prod]['prezzo'].values[0]
                        st.session_state.tavoli[t_sel].append({"nome": prod, "qta": qta, "prezzo": round(prz*qta, 2)})
                        st.rerun()
                
                with col2:
                    if st.session_state.tavoli[t_sel]:
                        st.table(pd.DataFrame(st.session_state.tavoli[t_sel]))
                        tot = round(sum(i['prezzo'] for i in st.session_state.tavoli[t_sel]), 2)
                        st.write(f"### TOTALE: {tot} €")
                        
                        if st.button("💰 PAGATO E STAMPA SCONTRINO"):
                            # 1. Stampa fisica
                            esegui_stampa_termica(t_sel, st.session_state.tavoli[t_sel], tot)
                            
                            # 2. Registra nel Database
                            p_str = ", ".join([f"{x['nome']}x{x['qta']}" for x in st.session_state.tavoli[t_sel]])
                            c.execute("INSERT INTO vendite (tavolo, piatti, totale, data) VALUES (?,?,?,?)",
                                      (t_sel, p_str, tot, datetime.now().strftime("%Y-%m-%d %H:%M")))
                            conn.commit()
                            
                            # 3. Libera tavolo e reset
                            st.session_state.tavoli[t_sel] = []
                            st.session_state.vista_tavolo = None
                            st.rerun()
            else:
                st.warning("Configura prima il menu!")

    elif mode == "Statistiche":
        st.header("📊 Incassi")
        st.dataframe(pd.read_sql_query("SELECT * FROM vendite", conn), use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.autenticato = False
        st.rerun()
