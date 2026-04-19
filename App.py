import streamlit as st
from datetime import datetime
try:
    from fpdf import FPDF
    PDF_SUPPORT = True
except:
    PDF_SUPPORT = False

# --- CONFIGURAZIONE STILE ---
st.set_page_config(page_title="HORECA PRO - KUBE DIRECT", layout="wide")

# --- FUNZIONE STAMPA OTTIMIZZATA PER CUSTOM KUBE 82.5mm ---
def genera_scontrino_kube(tavolo, ordine, totale):
    # Usiamo il formato 82.5mm specifico della tua Kube
    pdf = FPDF(format=(82.5, 120)) 
    pdf.add_page()
    pdf.set_margins(left=4, top=2, right=4)
    
    # Intestazione Bar
    pdf.set_font("Courier", "B", 14)
    pdf.cell(0, 10, "DOMENICO BAR", ln=True, align='C')
    
    pdf.set_font("Courier", "", 10)
    pdf.cell(0, 5, f"Tavolo: {tavolo}", ln=True, align='C')
    pdf.cell(0, 5, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True, align='C')
    pdf.cell(0, 5, "-"*28, ln=True, align='C')
    
    # Lista Prodotti
    pdf.set_font("Courier", "", 11)
    for item in ordine:
        nome = item['n'][:18]
        pdf.cell(48, 7, f"{nome}")
        pdf.cell(20, 7, f"{item['p']:.2f}", ln=True, align='R')
    
    pdf.cell(0, 5, "-"*28, ln=True, align='C')
    
    # Totale
    pdf.set_font("Courier", "B", 14)
    pdf.cell(0, 10, f"TOTALE: EUR {totale:.2f}", ln=True, align='R')
    
    # Spazio per la taglierina (fondamentale per Kube)
    pdf.cell(0, 15, ".", ln=True, align='C') 

    return pdf.output(dest='S').encode('latin-1')

# --- LOGICA DELL'APP ---
# (Qui ci sono i tuoi tavoli e le icone che abbiamo messo prima)

if 't_attivo' in st.session_state:
    t_corrente = st.session_state.t_attivo
    ordine_corrente = st.session_state.tavoli[t_corrente]
    totale_conto = sum(x['p'] for x in ordine_corrente)

    if totale_conto > 0:
        if PDF_SUPPORT:
            pdf_bytes = genera_scontrino_kube(t_corrente, ordine_corrente, totale_conto)
            
            # IL TASTO CHE USAREMO
            st.download_button(
                label="🖨️ STAMPA SCONTRINO KUBE",
                data=pdf_bytes,
                file_name=f"scontrino_{t_corrente}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
