import streamlit as st
import pandas as pd
import win32print
import win32ui
import socket
from datetime import datetime
import sqlite3
import os

# --- CONFIGURAZIONE STAMPANTE E RETE ---
# NOME ESATTO DELLA TUA STAMPANTE CUSTOM
NOME_STAMPANTE_KUBE = "Custom Kube 82,5mm (200dpi)" 
IP_FISSO = "192.168.90.235"
PORTA = "8501"

st.set_page_config(page_title="BAR RITROVO PRO", layout="wide", page_icon="🍹")

# --- STILE CSS PER TOUCH SCREEN ELO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 90px; font-size: 22px !important; }
    .cat-header { background-color: #333; color: orange; padding: 10px; border-radius: 10px; text-align: center; margin: 10px 0; font-size: 1.4em; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('bar_pro.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, nome TEXT, prezzo REAL, categoria TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS vendite (id INTEGER PRIMARY KEY, data TEXT, totale REAL, tavolo TEXT)')
    conn.commit()
    return conn

# --- FUNZIONE DI STAMPA DIRETTA SU CUSTOM KUBE ---
def invia_a_stampante(tavolo, piatti, totale):
    try:
        hprinter = win32print.OpenPrinter(NOME_STAMPANTE_KUBE)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(NOME_STAMPANTE_KUBE)
        
        pdc.StartDoc(f"Ordine_{tavolo}")
        pdc.StartPage()
        
        # Font Titolo (Grande per 82.5mm)
        f_tit = win32ui.CreateFont({"name": "Arial", "height": 70, "weight": 900})
        # Font Testo
        f_txt = win32ui.CreateFont({"name": "Arial", "height": 45, "weight": 400})
        
        y = 20
        pdc.SelectObject(f_tit)
        pdc.TextOut(20, y, "BAR RITROVO")
        
        y += 100
        pdc.SelectObject(f_txt)
        pdc.TextOut(20, y, f"TAVOLO: {tavolo}")
        y += 55
        pdc.TextOut(20, y, f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        y += 50
        pdc.TextOut(20, y, "-" * 30)
        
        y += 60
        for p in piatti:
            # Layout riga: Prodotto e Prezzo
            pdc.TextOut(20, y, f"{p['nome'][:15]:<15} {p['prezzo']:>6.2f}E")
            y += 55
            
        y += 40
        pdc.TextOut(20, y, "-" * 30)
        y += 80
        
        pdc.SelectObject(f_tit)
        pdc.TextOut(20, y, f"TOTALE: {totale:.2f} E")
        
        pdc.EndPage()
        pdc.EndDoc()
        del pdc
        return True
    except Exception as e:
        st.error(f"Errore: la stampante '{NOME_STAMPANTE_KUBE}' non è stata trovata. Controlla il nome esatto su Windows!")
        return False

# --- LOGICA APPLICAZIONE ---
conn = init_db()
if 'ordini_tavoli' not in st.session_state: st.session_state.ordini_tavoli = {}

with st.sidebar:
    st.title("🍹 CASSA PRO")
    st.info(f"🖨️ {NOME_STAMPANTE_KUBE}")
    st.success(f"📱 LINK: {IP_FISSO}:{PORTA}")
    pagina = st.radio("MENU:", ["💰 CASSA", "📋 PRODOTTI", "📈 INCASSI"])

if pagina == "💰 CASSA":
    if 'tavolo_aperto' not in st.session_state: st.session_state.tavolo_aperto = None

    if st.session_state.tavolo_aperto is None:
        st.header("Seleziona un Tavolo")
        tavoli = ["BANCO", "TAV 1", "TAV 2", "TAV 3", "TAV 4", "EST 1", "EST 2", "EST 3"]
        cols = st.columns(4)
        for i, t in enumerate(tavoli):
            colore = "🔴" if t in st.session_state.ordini_tavoli and st.session_state.ordini_tavoli[t] else "⚪"
            if cols[i % 4].button(f"{colore} {t}", key=f"t_{t}"):
                st.session_state.tavolo_aperto = t
                st.rerun()
    else:
        t_id = st.session_state.tavolo_aperto
        st.subheader(f"📍 Servizio: {t_id}")
        if st.button("⬅️ TORNA ALLA MAPPA"):
            st.session_state.tavolo_aperto = None
            st.rerun()

        col_m, col_o = st.columns([2, 1])
        
        with col_m:
            df_m = pd.read_sql_query("SELECT * FROM menu", conn)
            for cat in ["☕ CAFFÈ", "🍺 DRINK", "🍔 CIBO", "🍰 DOLCI"]:
                st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
                items = df_m[df_m['categoria'] == cat]
                c_btn = st.columns(3)
                for idx, row in items.reset_index().iterrows():
                    if c_btn[idx % 3].button(f"{row['nome']}\n{row['prezzo']:.2f}€", key=f"p_{row['id']}"):
                        if t_id not in st.session_state.ordini_tavoli: st.session_state.ordini_tavoli[t_id] = []
                        st.session_state.ordini_tavoli[t_id].append({"nome": row['nome'], "prezzo": row['prezzo']})
                        st.rerun()

        with col_o:
            st.write("🛒 **CARRELLO**")
            ordine = st.session_state.ordini_tavoli.get(t_id, [])
            for i, item in enumerate(ordine):
                c1, c2 = st.columns([4, 1])
                c1.write(f"{item['nome']} - {item['prezzo']:.2f}€")
                if c2.button("❌", key=f"del_{t_id}_{i}"):
                    st.session_state.ordini_tavoli[t_id].pop(i)
                    st.rerun()
            
            if ordine:
                totale = sum(x['prezzo'] for x in ordine)
                st.divider()
                st.header(f"TOT: {totale:.2f}€")
                if st.button("🖨️ STAMPA SCONTRINO", type="primary"):
                    if invia_a_stampante(t_id, ordine, totale):
                        conn.execute("INSERT INTO vendite (data, totale, tavolo) VALUES (?,?,?)", 
                                     (datetime.now().strftime('%Y-%m-%d %H:%M'), totale, t_id))
                        conn.commit()
                        st.session_state.ordini_tavoli[t_id] = []
                        st.session_state.tavolo_aperto = None
                        st.success("Stampa completata!")
                        st.rerun()

elif pagina == "📋 PRODOTTI":
    st.header("Gestione Listino")
    with st.form("new"):
        n = st.text_input("Nome Prodotto")
        p = st.number_input("Prezzo", step=0.10)
        c = st.selectbox("Categoria", ["☕ CAFFÈ", "🍺 DRINK", "🍔 CIBO", "🍰 DOLCI"])
        if st.form_submit_button("Aggiungi"):
            conn.execute("INSERT INTO menu (nome, prezzo, categoria) VALUES (?,?,?)", (n, p, c))
            conn.commit()
            st.rerun()

elif pagina == "📈 INCASSI":
    df_v = pd.read_sql_query("SELECT * FROM vendite", conn)
    st.metric("Totale Incassato", f"{df_v['totale'].sum():.2f} €")
    st.table(df_v)

# --- AVVIO SERVER ---
if __name__ == "__main__":
    os.system(f"streamlit run main.py --server.address=0.0.0.0 --server.port={PORTA}")
