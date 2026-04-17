import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
FOTO_BAR = "https://i.ibb.co/x8D75fP0/Domenico.jpg" 

st.set_page_config(page_title="Domenico Cashier", page_icon="💰", layout="wide")

# --- INIZIALIZZAZIONE STATO (Per non perdere i dati al click) ---
if 'conto_attuale' not in st.session_state:
    st.session_state.conto_attuale = []
if 'menu' not in st.session_state:
    # Qui puoi scrivere tu i tuoi prodotti predefiniti
    st.session_state.menu = {
        "Caffè": 1.20,
        "Cappuccino": 1.50,
        "Cornetto": 1.20,
        "Spritz": 5.00,
        "Birra": 4.00,
        "Panino": 6.00
    }

# --- STILE CSS ---
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    .product-btn { 
        border: none; padding: 10px; border-radius: 10px;
        background-color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center; cursor: pointer;
    }
    .scontrino-paper {
        background-color: white; padding: 20px; border-radius: 5px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        font-family: 'Courier New', Courier, monospace;
        color: #333;
    }
    .totale-big { font-size: 40px; font-weight: bold; color: #1e3d59; }
</style>
""", unsafe_allow_html=True)

# --- LAYOUT PRINCIPALE ---
col_menu, col_conto = st.columns([2, 1])

# --- COLONNA SINISTRA: MENU E AGGIUNTA ---
with col_menu:
    st.markdown(f"### 🍽️ Menu Digitale")
    
    # Sezione per aggiungere nuove pietanze al volo
    with st.expander("➕ Aggiungi/Modifica prodotto nel Menu"):
        c1, c2, c3 = st.columns([2, 1, 1])
        nuovo_nome = c1.text_input("Nome Pietanza")
        nuovo_prezzo = c2.number_input("Prezzo €", min_value=0.0, step=0.10)
        if c3.button("SALVA"):
            if nuovo_nome:
                st.session_state.menu[nuovo_nome] = nuovo_prezzo
                st.rerun()

    st.markdown("---")
    
    # Griglia di pulsanti per la vendita
    st.write("Clicca su un prodotto per aggiungerlo al conto:")
    cols = st.columns(3)
    for i, (nome, prezzo) in enumerate(st.session_state.menu.items()):
        if cols[i % 3].button(f"{nome}\n€{prezzo:.2f}", key=nome):
            st.session_state.conto_attuale.append({"nome": nome, "prezzo": prezzo})
            st.rerun()

# --- COLONNA DESTRA: SCONTRINO ---
with col_conto:
    st.markdown("### 🧾 Scontrino")
    
    with st.container():
        st.markdown('<div class="scontrino-paper">', unsafe_allow_html=True)
        st.markdown(f"<center><b>DOMENICO BAR</b><br>{datetime.now().strftime('%d/%m/%Y %H:%M')}</center><hr>", unsafe_allow_html=True)
        
        totale = 0.0
        if not st.session_state.conto_attuale:
            st.write("Scontrino vuoto")
        else:
            for item in st.session_state.conto_attuale:
                st.write(f"{item['nome']} --- €{item['prezzo']:.2f}")
                totale += item['prezzo']
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:right;'>TOTALE: <span class='totale-big'>€{totale:.2f}</span></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Pulsanti di azione
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ SVUOTA CONTO"):
        st.session_state.conto_attuale = []
        st.rerun()
        
    if st.button("✅ CHIUDI E INVIA ORDINE"):
        if st.session_state.conto_attuale:
            st.success("Ordine registrato!")
            st.balloons()
            # Prepariamo il testo per la mail
            lista_mail = "\n".join([f"- {item['nome']}: €{item['prezzo']:.2f}" for item in st.session_state.conto_attuale])
            form_html = f"""
                <form action="https://formsubmit.co/{TUA_EMAIL}" method="POST" id="f_bar">
                    <input type="hidden" name="ORDINE" value="{lista_mail}">
                    <input type="hidden" name="TOTALE" value="€ {totale:.2f}">
                    <input type="hidden" name="_captcha" value="false">
                </form>
                <script>document.getElementById('f_bar').submit();</script>"""
            st.components.v1.html(form_html, height=0)
            st.session_state.conto_attuale = [] # Resetta dopo l'invio
        else:
            st.error("Il conto è vuoto!")

st.markdown("<br><hr><center>© 2026 Domenico Business Management</center>", unsafe_allow_html=True)
