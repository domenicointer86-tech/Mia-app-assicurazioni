import streamlit as st
from datetime import datetime

# --- CONFIGURAZIONE ---
TUA_EMAIL = "domenicointer86@gmail.com" 
FOTO_BAR = "https://i.ibb.co/x8D75fP0/Domenico.jpg" 
LOGO_BAR = "https://cdn-icons-png.flaticon.com/512/924/924514.png"

st.set_page_config(page_title="Domenico Bar - Gestione", page_icon="☕")

# --- INIZIALIZZAZIONE MENU (Se non esiste già nella sessione) ---
if 'menu_salvato' not in st.session_state:
    st.session_state.menu_salvato = {
        "Caffetteria": {"Caffè": 1.20, "Cappuccino": 1.50, "Cornetto": 1.20},
        "Drink": {"Spritz": 5.00, "Birra": 4.50},
        "Food": {"Panino": 6.00, "Tagliere": 12.00}
    }

# --- STILE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    .stButton>button { width: 100%; border-radius: 15px; background: #8B4513; color: white; border: none; }
    .bill-box { background: #fff8e1; padding: 15px; border-radius: 15px; border: 2px dashed #8B4513; text-
