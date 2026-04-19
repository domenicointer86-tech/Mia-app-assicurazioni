import streamlit as st
from datetime import datetime
try:
    from fpdf import FPDF
    PDF_SUPPORT = True
except:
    PDF_SUPPORT = False

# --- FUNZIONE SPECIFICA PER CUSTOM KUBE 82.5mm ---
def genera_scontrino_kube(tavolo, ordine, totale):
    # 82.5mm di larghezza. L'altezza (200) è il limite massimo del foglio.
    pdf = FPDF(format=(82.5, 200)) 
    pdf.add_page()
    
    # Margini laterali ridotti per sfruttare la testina da 200dpi
    pdf.set_margins(left=4, top=4, right=4)
    pdf.set_auto_page_break(False)
    
    # Nome del Bar (Grande e Grassetto)
    pdf.set_font("Courier", "B", 16)
    pdf.cell(0, 10, "DOMENICO BAR", ln=True, align='C')
    
    # Info Tavolo
    pdf.set_font("Courier", "", 10)
    pdf.cell(0, 5, f"TAVOLO: {tavolo}", ln=True, align='C')
    pdf.cell(0, 5, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True, align='C')
    pdf.cell(0, 5, "="*34, ln=True, align='C') # Linea di separazione
    
    # Elenco Prodotti
    pdf.set_font("Courier", "", 12)
    for item in ordine:
        nome_prod = item['n'][:22] # Più spazio per il nome grazie ai 82.5mm
        prezzo_prod = f"{item['p']:.2f}"
        # Nome a sinistra, prezzo a destra
        pdf.cell(48, 8, f"{nome_prod}")
        pdf.cell(24, 8, f"EUR {prezzo_prod}", ln=True, align='R')
    
    pdf.cell(0, 5, "="*34, ln=True, align='C')
    
    # Totale Scontrino
    pdf.set_font("Courier", "B", 16)
    pdf.cell(0, 15, f"TOTALE: EUR {totale:.2f}", ln=True, align='R')
    
    # Spazio per la taglierina automatica Kube
    pdf.cell(0, 20, "", ln=True) 
    pdf.set_font("Courier", "I", 9)
    pdf.cell(0, 5, "Grazie e Arrivederci!", ln=True, align='C')
    pdf.cell(0, 10, ".", ln=True, align='C') # Punto finale per trascinare la carta oltre la taglierina

    return pdf.output(dest='S').encode('latin-1')

# --- TASTO NELL'APP ---
if PDF_SUPPORT:
    pdf_bytes = genera_scontrino_kube(t_sel, ordine, tot)
    st.download_button(
        label="🖨️ STAMPA SCONTRINO (KUBE)",
        data=pdf_bytes,
        file_name=f"scontrino_{t_sel}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
