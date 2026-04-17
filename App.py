import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
# Puoi cambiare questa foto con quella del tuo bar o lasciare la tua
FOTO_BAR = "https://i.ibb.co/x8D75fP0/Domenico.jpg" 
LOGO_BAR = "https://cdn-icons-png.flaticon.com/512/924/924514.png" # Icona Bar/Cocktail

st.set_page_config(page_title="Gestione Bar - Domenico", page_icon="☕", layout="centered")

# --- DATABASE MENU ---
MENU = {
    "Caffetteria": {"Caffè": 1.20, "Cappuccino": 1.50, "Cornetto": 1.20},
    "Drink": {"Spritz": 5.00, "Birra Media": 4.50, "Coca Cola": 2.50},
    "Food": {"Panino": 6.00, "Insalata": 7.00, "Tagliere": 12.00}
}

# --- STILE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    .stButton>button {
        width: 100%; border-radius: 15px;
        background: #8B4513; color: white; font-weight: bold; height: 3em; border: none;
    }
    .bill-box {
        background: #fff8e1; padding: 20px; border-radius: 15px;
        border: 2px dashed #8B4513; text-align: center;
    }
    .total-price { font-size: 30px; font-weight: bold; color: #8B4513; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col1, col2, col3 = st.columns([1, 1.5, 1])
with col1:
    st.image(FOTO_BAR, width=80)
with col2:
    st.markdown("<h2 style='text-align:center; color:#8B4513;'>DOMENICO BAR</h2>", unsafe_allow_html=True)
with col3:
    st.image(LOGO_BAR, width=60)

# --- NAVIGAZIONE ---
tab1, tab2 = st.tabs(["🛒 ORDINAZIONE & CONTO", "📅 PRENOTA TAVOLO"])

# --- TAB 1: ORDINAZIONE ---
with tab1:
    st.markdown("### 📝 Prendi l'ordine")
    tavolo = st.selectbox("Seleziona Tavolo", [f"Tavolo {i}" for i in range(1, 11)] + ["Asporto"])
    
    scelte = []
    col_a, col_b = st.columns(2)
    
    with col_a:
        categoria = st.selectbox("Categoria", list(MENU.keys()))
    
    prodotti_cat = MENU[categoria]
    prodotto = st.multiselect("Cosa desideri?", list(prodotti_cat.keys()))
    
    totale = sum(prodotti_cat[p] for p in prodotto)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='bill-box'>
            <p>Riepilogo {tavolo}</p>
            <div class='total-price'>€ {totale:.2f}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("INVIA ORDINE IN CASSA"):
        if prodotto:
            st.success(f"Ordine inviato per il {tavolo}!")
            st.balloons()
            # Invio mail dell'ordine
            ordine_testo = ", ".join(prodotto)
            html_ordine = f"""
                <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="fo">
                    <input type="hidden" name="Tavolo" value="{tavolo}">
                    <input type="hidden" name="Ordine" value="{ordine_testo}">
                    <input type="hidden" name="Totale" value="€ {totale:.2f}">
                    <input type="hidden" name="_captcha" value="false">
                </form>
                <script>document.getElementById('fo').submit();</script>
            """
            st.components.v1.html(html_ordine, height=0)

# --- TAB 2: PRENOTAZIONI ---
with tab2:
    st.markdown("### 📅 Prenota un tavolo")
    with st.form("prenotazione_bar"):
        nome_p = st.text_input("Nome Prenotazione*")
        persone = st.number_input("Numero persone", min_value=1, max_value=20, value=2)
        data_p = st.date_input("Data", min_value=datetime.today())
        ora_p = st.time_input("Orario")
        tel_p = st.text_input("Cellulare")
        
        submit_p = st.form_submit_button("CONFERMA PRENOTAZIONE")
        
    if submit_p:
        if nome_p and tel_p:
            st.success(f"Tavolo prenotato per {nome_p}!")
            # Invio mail prenotazione
            html_p = f"""
                <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="fp">
                    <input type="hidden" name="Tipo" value="PRENOTAZIONE TAVOLO">
                    <input type="hidden" name="Nome" value="{nome_p}">
                    <input type="hidden" name="Persone" value="{persone}">
                    <input type="hidden" name="Quando" value="{data_p} {ora_p}">
                    <input type="hidden" name="Telefono" value="{tel_p}">
                    <input type="hidden" name="_captcha" value="false">
                </form>
                <script>document.getElementById('fp').submit();</script>
            """
            st.components.v1.html(html_p, height=0)
        else:
            st.error("Inserisci Nome e Telefono!")

st.markdown("<br><hr><center>© 2026 Domenico Bar & Bistrot</center>", unsafe_allow_html=True)
