def crea_pdf(tavolo, piatti, totale):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Intestazione
    pdf.cell(200, 10, txt=f"RICEVUTA - {tavolo}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(10)
    
    # Tabella piatti
    for p in piatti:
        # Sostituiamo caratteri speciali per evitare l'errore Unicode
        nome_pulito = p['nome'].replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
        pdf.cell(150, 10, txt=f"{nome_pulito}", border=1)
        pdf.cell(40, 10, txt=f"{p['prezzo']} Euro", border=1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    # Usiamo "Euro" invece del simbolo €
    pdf.cell(200, 10, txt=f"TOTALE DA PAGARE: {totale} Euro", ln=True)
    
    # Ritorna il PDF come stringa di byte
    return pdf.output(dest='S').encode('latin-1', errors='replace')
