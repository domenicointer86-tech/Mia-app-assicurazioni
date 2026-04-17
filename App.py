import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
FOTO_BAR = "https://i.ibb.co/x8D75fP0/Domenico.jpg" 

st.set_page_config(page_title="Domenico Bar", page_icon="☕")

# --- DATABASE MENU ---
MENU = {
    "Caffetteria": {"Caffè": 1.20, "Cappuccino": 1.50, "Cornetto": 1.20},
    "Drink": {"Spritz": 5.00, "Birra": 4.50, "Coca Cola": 2.50},
    "Food": {"Panino": 6.00, "Insalata": 7.00, "Tagliere": 12.00}
}

# --- STILE CSS ---
st.markdown("""
<style>
.stApp { background-color: #fdfdfd; }
.stButton>button { width: 100%; border-radius: 15px; background: #8B4513; color: white; }
.scontrino { background: #fff8e1; padding: 15px; border-radius: 10px; border: 2px dashed #8B4513; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.image(FOTO_BAR, width=80)
st.title("DOMENICO BAR")

# --- NAVIGAZIONE ---
tab1, tab2 = st.tabs(["🛒 Ordini", "📅 Prenotazioni"])

with tab1:
    st.subheader("Nuovo Ordine")
    tavolo = st.selectbox("Tavolo", [f"Tavolo {i}" for i in range(1, 11)])
    cat = st.selectbox("Categoria", list(MENU.keys()))
    scelti = st.multiselect("Prodotti", list(MENU[cat].keys()))
    
    totale = sum(MENU[cat][p] for p in scelti)
    st.markdown(f"<div class='scontrino'><h3>TOTALE</h3><h1>€ {totale:.2f}</h1></div>", unsafe_allow_html=True)
    
    if st.button("INVIA ORDINE"):
        if scelti:
            st.success("Inviato!")
            st.balloons()
            ordine_txt = ", ".join(scelti)
            form = f"""
            <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="f1">
                <input type="hidden" name="Tavolo" value="{tavolo}">
                <input type="hidden" name="Ordine" value="{ordine_txt}">
                <input type="hidden" name="Totale" value="{totale}">
            </form>
            <script>document.getElementById('f1').submit();</script>"""
            st.components.v1.html(form, height=0)

with tab2:
    st.subheader("Prenota Tavolo")
    with st.form("f2"):
        nome = st.text_input("Nome*")
        tel = st.text_input("Tel*")
        dt = st.date_input("Data", min_value=datetime.today())
        ora = st.time_input("Ora")
        if st.form_submit_button("CONFERMA"):
            if nome and tel:
                st.success("Prenotato!")
                form2 = f"""
                <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="f2">
                    <input type="hidden" name="Prenotazione" value="{nome}">
                    <input type="hidden" name="Quando" value="{dt} {ora}">
                </form>
                <script>document.getElementById('f2').submit();</script>"""
                st.components.v1.html(form2, height=0)
