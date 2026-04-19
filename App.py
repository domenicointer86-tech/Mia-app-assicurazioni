import streamlit as st
from datetime import datetime
try:
    from fpdf import FPDF
    PDF_SUPPORT = True
except:
    PDF_SUPPORT = False

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="HORECA PRO - STAMPA TERMICA", layout="wide")

# --- FUNZIONE STAMPA TERMICA PROFESSIONALE (58mm) ---
def genera_scontrino_termico(tavolo, ordine, totale):
    # Formato 58mm larghezza, altezza dinamica. Margini quasi a zero.
    pdf = FPDF(format=(58, 150)) 
    pdf.add_page()
    pdf.set_margins(left=2, top=2, right=2)
    pdf.set_auto_page_break(False)
    
    # Intestazione (Nome Bar)
    pdf.set_font("Courier", "B", 12)
    pdf.cell(0, 8, "DOMENICO BAR", ln=True, align='C')
    
    # Info Tavolo e Data
    pdf.set_font("Courier", "", 8)
    pdf.cell(0, 4, f"Tavolo: {tavolo}", ln=True, align='C')
    pdf.cell(0, 4, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True, align='C')
    pdf.cell(0, 4, "-"*28, ln=True, align='C')
    
    # Lista Prodotti (Formattazione incolonnata)
    pdf.set_font("Courier", "", 9)
    for item in ordine:
        # Nome prodotto max 14 lettere per non sballare la riga
        nome = item['n'][:14]
        prezzo = f"{item['p']:.2f}"
        pdf.cell(38, 5, f"{nome}")
        pdf.cell(12, 5, f"{prezzo}", ln=True, align='R')
    
    pdf.cell(0, 4, "-"*28, ln=True, align='C')
    
    # Totale in grassetto
    pdf.set_font("Courier", "B", 12)
    pdf.cell(0, 10, f"TOTALE: EUR {totale:.2f}", ln=True, align='R')
    
    # Messaggio finale
    pdf.set_font("Courier", "I", 7)
    pdf.cell(0, 10, "Grazie e a presto!", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- LOGICA APPLICAZIONE ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "☕ CAFFETTERIA": {"Caffè": {"p": 1.2, "img": "☕"}, "Cornetto": {"p": 1.5, "img": "🥐"}},
        "🍷 BEVANDE": {"Acqua": {"p": 1.0, "img": "💧"}, "Birra": {"p": 3.5, "img": "🍺"}}
    }
if 'tavoli' not in st.session_state:
    st.session_state.tavoli = {f"TAVOLO {i}": [] for i in range(1, 13)}

# --- INTERFACCIA ---
st.title("🏨 HORECA POS - STAMPA")

# Selezione Tavoli
t_cols = st.columns(4)
for i, (t_nome, items) in enumerate(st.session_state.tavoli.items()):
    if t_cols[i%4].button(f"{t_nome}\n€{sum(x['p'] for x in items):.2f}" if items else f"{t_nome}\nLIBERO", key=t_nome):
        st.session_state.t_attivo = t_nome

if 't_attivo' in st.session_state:
    t_sel = st.session_state.t_attivo
    st.divider()
    c_menu, c_conto = st.columns([2, 1])

    with c_menu:
        st.subheader(f"Menu {t_sel}")
        tabs = st.tabs(list(st.session_state.menu.keys()))
        for i, cat in enumerate(st.session_state.menu.keys()):
            with tabs[i]:
                m_cols = st.columns(3)
                for j, (prod, dati) in enumerate(st.session_state.menu[cat].items()):
                    if m_cols[j%3].button(f"{dati['img']}\n{prod}", key=f"add_{cat}_{prod}"):
                        st.session_state.tavoli[t_sel].append({"n": prod, "p": dati['p']})
                        st.rerun()

    with c_conto:
        st.subheader("Conto")
        ordine = st.session_state.tavoli[t_sel]
        tot = sum(x['p'] for x in ordine)
        for item in ordine:
            st.write(f"{item['n']} - €{item['p']:.2f}")
        
        if tot > 0:
            st.markdown(f"### TOTALE: €{tot:.2f}")
            
            # --- TASTO STAMPA ---
            if PDF_SUPPORT:
                pdf_bytes = genera_scontrino_termico(t_sel, ordine, tot)
                st.download_button(
                    label="🖨️ STAMPA SCONTRINO",
                    data=pdf_bytes,
                    file_name=f"scontrino_{t_sel}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            if st.button("✅ CHIUDI TAVOLO", type="primary", use_container_width=True):
                st.session_state.tavoli[t_sel] = []
                st.success("Incassato!")
                st.rerun()
