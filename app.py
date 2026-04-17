import streamlit as st
from datetime import datetime
from fpdf import FPDF
import base64

# --- FUNZIONE GENERAZIONE PDF PER STAMPANTE TERMICA ---
def genera_pdf_scontrino(tavolo, ordini, totale):
    pdf = FPDF(format=(58, 150)) # Formato standard carta termica 58mm
    pdf.add_page()
    pdf.set_font("Courier", "B", 12)
    pdf.cell(0, 10, "DOMENICO RISTO-PRO", ln=True, align='C')
    pdf.set_font("Courier", "", 9)
    pdf.cell(0, 5, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.cell(0, 5, f"Tavolo: {tavolo}", ln=True, align='C')
    pdf.cell(0, 5, "-"*25, ln=True, align='C')
    
    for item in ordini:
        pdf.cell(30, 5, f"{item['n'][:15]}")
        pdf.cell(10, 5, f"{item['pr']:.2f}", align='R', ln=True)
    
    pdf.cell(0, 5, "-"*25, ln=True, align='C')
    pdf.set_font("Courier", "B", 12)
    pdf.cell(30, 10, "TOTALE")
    pdf.cell(10, 10, f"Euro {totale:.2f}", align='R', ln=True)
    pdf.set_font("Courier", "", 8)
    pdf.cell(0, 10, "Grazie e a presto!", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- LOGICA APP ---
if 'menu' not in st.session_state:
    st.session_state.menu = {"Cucina": {"Pizza": 8.0, "Pasta": 10.0}, "Bar": {"Birra": 5.0, "Caffè": 1.2}}
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"Tavolo {i}": [] for i in range(1, 13)}

st.set_page_config(page_title="Domenico Pro", layout="wide")
st.title("🚀 Domenico Management & Print")

t_sel = st.selectbox("Seleziona Tavolo:", list(st.session_state.tavoli.keys()))
col_a, col_b = st.columns([2, 1])

with col_a:
    for cat, prodotti in st.session_state.menu.items():
        st.write(f"**{cat}**")
        p_cols = st.columns(3)
        for j, (p, prezzo) in enumerate(prodotti.items()):
            if p_cols[j % 3].button(f"{p}\n€{prezzo}", key=f"{t_sel}_{p}"):
                st.session_state.tavoli[t_sel].append({"n": p, "pr": prezzo})
                st.rerun()

with col_b:
    st.write(f"### 🧾 Conto {t_sel}")
    conto = st.session_state.tavoli[t_sel]
    tot = sum(item['pr'] for item in conto)
    for item in conto:
        st.write(f"- {item['n']}: €{item['pr']:.2f}")
    st.divider()
    st.write(f"**TOTALE: €{tot:.2f}**")
    
    if tot > 0:
        # Genera il PDF dello scontrino
        pdf_data = genera_pdf_scontrino(t_sel, conto, tot)
        
        st.download_button(
            label="🖨️ STAMPA SCONTRINO",
            data=pdf_data,
            file_name=f"scontrino_{t_sel}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        if st.button("PAGA E CHIUDI", type="primary", use_container_width=True):
            st.session_state.tavoli[t_sel] = []
            st.success("Tavolo liberato!")
            st.rerun()
