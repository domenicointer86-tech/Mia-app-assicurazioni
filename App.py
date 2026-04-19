import streamlit as st
from datetime import datetime
try:
    from fpdf import FPDF
    PDF_SUPPORT = True
except:
    PDF_SUPPORT = False

# --- CONFIGURAZIONE SPECIFICA CUSTOM KUBE 82.5mm ---
def genera_scontrino_kube(tavolo, ordine, totale):
    pdf = FPDF(format=(82.5, 150)) 
    pdf.add_page()
    pdf.set_margins(left=5, top=5, right=5)
    pdf.set_font("Courier", "B", 14)
    pdf.cell(0, 10, "DOMENICO BAR", ln=True, align='C')
    pdf.set_font("Courier", "", 10)
    pdf.cell(0, 5, f"Tavolo: {tavolo}", ln=True, align='C')
    pdf.cell(0, 5, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True, align='C')
    pdf.cell(0, 5, "-"*30, ln=True, align='C')
    pdf.set_font("Courier", "", 11)
    for item in ordine:
        pdf.cell(45, 7, f"{item['n'][:18]}")
        pdf.cell(20, 7, f"E {item['p']:.2f}", ln=True, align='R')
    pdf.cell(0, 5, "-"*30, ln=True, align='C')
    pdf.set_font("Courier", "B", 14)
    pdf.cell(0, 10, f"TOTALE: EUR {totale:.2f}", ln=True, align='R')
    pdf.cell(0, 15, "", ln=True) 
    return pdf.output(dest='S').encode('latin-1')

# --- INIZIALIZZAZIONE ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "☕ CAFFETTERIA": {"Caffè": {"p": 1.2, "img": "☕"}, "Cornetto": {"p": 1.5, "img": "🥐"}},
        "🍷 BEVANDE": {"Acqua": {"p": 1.0, "img": "💧"}, "Birra": {"p": 3.5, "img": "🍺"}}
    }
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"TAVOLO {i}": [] for i in range(1, 13)}
if 'incasso' not in st.session_state:
    st.session_state.incasso = 0.0

# --- INTERFACCIA ---
st.title("🏨 HORECA POS - CUSTOM KUBE")

t_cols = st.columns(4)
for i, (t_nome, items) in enumerate(st.session_state.tavoli.items()):
    if t_cols[i%4].button(f"{t_nome}\n€{sum(x['p'] for x in items):.2f}" if items else f"{t_nome}\nLIBERO", key=t_nome):
        st.session_state.t_attivo = t_nome

# CONTROLLO: Esiste un tavolo attivo?
if 't_attivo' in st.session_state:
    t_corrente = st.session_state.t_attivo  # <--- Qui definiamo la variabile che mancava
    st.divider()
    c_menu, c_conto = st.columns([2, 1])

    with c_menu:
        st.subheader(f"Ordine {t_corrente}")
        tabs = st.tabs(list(st.session_state.menu.keys()))
        for i, cat in enumerate(st.session_state.menu.keys()):
            with tabs[i]:
                m_cols = st.columns(3)
                for j, (prod, dati) in enumerate(st.session_state.menu[cat].items()):
                    if m_cols[j%3].button(f"{dati['img']}\n{prod}", key=f"btn_{cat}_{prod}"):
                        st.session_state.tavoli[t_corrente].append({"n": prod, "p": dati['p']})
                        st.rerun()

    with c_conto:
        st.subheader("Conto")
        ordine_corrente = st.session_state.tavoli[t_corrente]
        totale_conto = sum(x['p'] for x in ordine_corrente)
        
        for item in ordine_corrente:
            st.write(f"• {item['n']} - €{item['p']:.2f}")
        
        if totale_conto > 0:
            st.markdown(f"### TOTALE: €{totale_conto:.2f}")
            
            # STAMPA (Usando le variabili corrette)
            if PDF_SUPPORT:
                pdf_bytes = genera_scontrino_kube(t_corrente, ordine_corrente, totale_conto)
                st.download_button(
                    label="🖨️ STAMPA SCONTRINO (KUBE)",
                    data=pdf_bytes,
                    file_name=f"scontrino_{t_corrente}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            if st.button("✅ CHIUDI E INCASSA", type="primary", use_container_width=True):
                st.session_state.incasso += totale_conto
                st.session_state.tavoli[t_corrente] = []
                st.rerun()
