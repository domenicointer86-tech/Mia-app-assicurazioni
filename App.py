import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# --- Database Setup ---
conn = sqlite3.connect('ristorante_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vendite 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, piatto TEXT, prezzo REAL, data TEXT)''')
conn.commit()

# --- Funzioni Business ---
def salva_vendita(piatti):
    data_ora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for p in piatti:
        c.execute("INSERT INTO vendite (piatto, prezzo, data) VALUES (?, ?, ?)", 
                  (p['piatto'], p['prezzo'], data_ora))
    conn.commit()

# --- Interfaccia Streamlit ---
st.set_page_config(page_title="Gestione Ristorante 2.0", layout="wide")

tab1, tab2 = st.tabs(["🛒 Gestione Sala", "📊 Analisi Vendite"])

with tab1:
    # (Qui tieni la logica dei tavoli che abbiamo scritto prima)
    # Ma quando clicchi su "Paga e Libera Tavolo", aggiungi:
    # salva_vendita(st.session_state.ordini[tavolo_conto])
    st.info("Gestisci i tavoli e salva gli ordini nel database locale.")

with tab2:
    st.header("Statistiche Professionali")
    df = pd.read_sql_query("SELECT * FROM vendite", conn)
    
    if not df.empty:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Top Piatti")
            fig = px.pie(df, names='piatto', values='prezzo', hole=0.3)
            st.plotly_chart(fig)
            
        with col_b:
            st.subheader("Incassi nel Tempo")
            df['data'] = pd.to_datetime(df['data'])
            df_daily = df.resample('D', on='data').sum()
            st.line_chart(df_daily['prezzo'])
            
        st.subheader("Storico Transazioni")
        st.dataframe(df.sort_values(by='data', ascending=False), use_container_width=True)
    else:
        st.warning("Ancora nessuna vendita registrata.")
