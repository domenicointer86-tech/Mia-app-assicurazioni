elif app_mode == "Magazzino":
        st.header("📦 Gestione Scorte & Analytics")
        
        # Statistiche rapide in alto
        df_mag = pd.read_sql_query("SELECT * FROM magazzino", conn)
        if not df_mag.empty:
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.subheader("Stato Attuale Scorte")
                # Grafico a barre orizzontali per le scorte
                st.bar_chart(df_mag.set_index('prodotto')['quantita'])
            
            with col_stat2:
                st.subheader("Prodotti Critici (<5 unità)")
                critici = df_mag[df_mag['quantita'] < 5]
                if not critici.empty:
                    st.error(f"Attenzione! {len(critici)} prodotti quasi esauriti.")
                    st.table(critici)
                else:
                    st.success("Tutte le scorte sono a livelli ottimali.")

        st.divider()

        # Sezione Caricamento
        st.subheader("➕ Carica Nuovi Prodotti")
        with st.form("carico_form", clear_on_submit=True):
            p_nome = st.text_input("Nome Prodotto esatto (come nel Menu)")
            p_qta = st.number_input("Unità da aggiungere", min_value=1, value=10)
            if st.form_submit_button("Aggiorna Inventario"):
                c.execute("INSERT OR REPLACE INTO magazzino (prodotto, quantita) VALUES (?, COALESCE((SELECT quantita FROM magazzino WHERE prodotto = ?), 0) + ?)", (p_nome, p_nome, p_qta))
                conn.commit()
                st.success(f"Caricate {p_qta} unità di {p_nome}")
                st.rerun()

    elif app_mode == "Dashboard Incassi":
        st.header("📊 Performance del Locale")
        df_vendite = pd.read_sql_query("SELECT * FROM vendite", conn)
        
        if not df_vendite.empty:
            # KPI principali
            m1, m2, m3 = st.columns(3)
            m1.metric("Incasso Totale", f"{df_vendite['totale'].sum()} €")
            m2.metric("Ordini Chiusi", len(df_vendite))
            m3.metric("Media per Tavolo", f"{round(df_vendite['totale'].mean(), 2)} €")

            # Grafico Vendite nel tempo
            st.subheader("Andamento Incassi")
            df_vendite['data'] = pd.to_datetime(df_vendite['data'])
            incassi_tempo = df_vendite.resample('D', on='data').sum()
            st.line_chart(incassi_tempo['totale'])

            # Analisi Piatti più venduti
            st.subheader("Analisi Prodotti")
            # Splittiamo la stringa dei piatti per contarli singolarmente
            tutti_i_piatti = []
            for p_string in df_vendite['piatti']:
                tutti_i_piatti.extend(p_string.split(", "))
            
            df_piatti = pd.Series(tutti_i_piatti).value_counts().reset_index()
            df_piatti.columns = ['Piatto', 'Vendite']
            st.bar_chart(df_piatti.set_index('Piatto'))
            
        else:
            st.warning("Nessun dato di vendita disponibile. Inizia a chiudere qualche tavolo!")
