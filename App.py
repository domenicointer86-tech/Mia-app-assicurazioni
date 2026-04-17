import streamlit as st
from datetime import datetime

# --- CONFIG ---
TUA_EMAIL = "domenicointer86@gmail.com" 
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 11)}
if 'menu' not in st.session_state:
    st.session_state.menu = {"Caffè": 1.2, "Spritz": 5.0, "Birra": 4.0, "Panino": 6.0}

st.set_page_config(page_title="Domenico Bar", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .t-rosso { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 10px; text-align: center; margin: 5px; }
    .t-verde { background-color: #28a745; color: white; padding: 10px; border-radius: 10px; text-align: center; margin: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🏨 Gestione Sala Domenico")

# --- PARTE ALTA: GESTIONE ---
tavolo_sel = st.selectbox("Seleziona Tavolo", list(st.session_state.tavoli.keys()))

col1, col2 = st.columns([2, 1])

with col1:
    st.write(f"### Ordina per {tavolo_sel}")
    c = st.columns(3)
    for i, (nome, prezzo) in enumerate(st.session_state.menu.items()):
        if c[i % 3].button(f"{nome} - €{prezzo}", key=f"btn_{nome}"):
            st.session_state.tavoli[tavolo_sel].append({"n": nome, "p": prezzo})
            st.rerun()

with col2:
    st.write("### Conto")
    tot = 0.0
    for item in st.session_state.tavoli[tavolo_sel]:
        st.write(f"{item['n']} - €{item['p']}")
        tot += item['p']
    st.write(f"**TOTALE: €{tot:.2f}**")
    if st.button("CHIUDI E PULISCI"):
        st.session_state.tavoli[tavolo_sel] = []
        st.success("Tavolo liberato!")
        st.rerun()

st.markdown("---")

# --- PARTE BASSA: MONITOR TAVOLI (Quella che non vedevi) ---
st.write("### 📊 STATO TAVOLI IN TEMPO REALE")
cols_sala = st.columns(5)
for i, (t_nome, t_lista) in enumerate(st.session_state.tavoli.items()):
    if t_lista: # Se ci sono ordini
        cols_sala[i % 5].markdown(f"<div class='t-rosso'><b>{t_nome}</b><br>OCCUPATO</div>", unsafe_allow_html=True)
    else:
        cols_sala[i % 5].markdown(f"<div class='t-verde'><b>{t_nome}</b><br>LIBERO</div>", unsafe_allow_html=True)
