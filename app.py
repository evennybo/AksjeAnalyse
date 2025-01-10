import streamlit as st
from services.data_fetcher import (
    fetch_stock_data, fetch_company_details, fetch_macro_data_combined,
    fetch_combined_geopolitical_news, fetch_news
)
from services.gpt_analysis import generate_combined_analysis
from services.visualizations import (
    plot_candlestick_chart_with_indicators, display_news_carousel, display_fundamental_analysis
)
from services.technical_indicators import add_bollinger_bands, calculate_rsi, calculate_macd


def main():
    st.title("Finansiell Analyseplattform")
    st.warning("**Disclaimer:** Denne plattformen tilbyr ikke finansiell rådgivning. Alle analyser er generert for informasjonsformål. Gjør alltid din egen vurdering før du tar økonomiske beslutninger.")
    st.subheader("Analyser aksjer med AI og tekniske indikatorer")
    
    # Initialiser session state
    if 'news_index' not in st.session_state:
        st.session_state['news_index'] = 0

    if 'fetch_count' not in st.session_state:
        st.session_state['fetch_count'] = 0

    # Input for aksjesymbol
    ticker = st.text_input("Skriv aksjesymbol (f.eks. EQNR, AAPL):")
    MAX_FETCHES_PER_DAY = 20  # Maks antall fetches per dag

    if st.session_state['fetch_count'] >= MAX_FETCHES_PER_DAY:
        st.warning("Du har nådd maksgrensen på 10 analyser i dag. Kom tilbake i morgen!")
    else:
        # Øk antall fetches med én
        st.session_state['fetch_count'] += 1


        # Hent data-knapp
        if st.button("Hent Analyse"):
            if ticker:
                try:
                    with st.spinner('Henter data...'):
                        # Hent aksje- og fundamentaldata
                        stock_data, fundamental_data = fetch_stock_data(ticker)
                        company_details = fetch_company_details(ticker)

                        # Beregn aksjepris
                        company_name = company_details["name"]
                        current_price = stock_data['Close'].iloc[-1] if not stock_data.empty else "N/A"
                        current_price_nok = round(current_price, 2) if current_price != "N/A" else "N/A"

                        # Vis informasjon om selskapet
                        st.info(f"**Selskap:** {company_name}\n\n\n**Dagens Aksjepris:** {current_price_nok} NOK")

                        # Hent øvrige data
                        macro_data = fetch_macro_data_combined(company_details["country"])
                        geopolitical_news = fetch_combined_geopolitical_news(company_details)
                        news_data = fetch_news(ticker)

                        print("######### GEOPOLITISK NEWS", macro_data)


                        # # Debugging: Sjekk nyhetsdata
                        # st.subheader("Sjekker Nyheter")
                        # if news_data:
                        #     st.write("Ticker-relaterte nyheter:")
                        #     for news in news_data:
                        #         st.write(f"- {news['title']} (Publisert: {news.get('published_date', 'N/A')})")
                        # else:
                        #     st.write("Ingen relevante nyheter funnet.")

                        # if geopolitical_news:
                        #     st.write("Geopolitiske nyheter:")
                        #     for news in geopolitical_news:
                        #         st.write(f"- {news['title']} (Publisert: {news.get('published_date', 'N/A')})")
                        # else:
                        #     st.write("Ingen geopolitiske nyheter funnet.")

                        # Beregn tekniske indikatorer
                        stock_data = add_bollinger_bands(stock_data)
                        stock_data = calculate_rsi(stock_data)
                        stock_data = calculate_macd(stock_data)

                        # Lagre i session state
                        st.session_state.update({
                            'ticker': ticker,
                            'stock_data': stock_data,
                            'fundamental_data': fundamental_data,
                            'macro_data': macro_data,
                            'geopolitical_news': geopolitical_news,
                            'news_data': news_data,
                            'company_details': company_details,
                            'combined_analysis': " "
                        })

                        #st.success("Data hentet! Klikk 'Generer AI-Analyse' for dypere analyse.")
                except Exception as e:
                    st.error(f"Noe gikk galt: {e}")
            else:
                st.warning("Skriv inn et gyldig aksjesymbol.")

        # Velg tekniske indikatorer
        if 'stock_data' in st.session_state:
            with st.sidebar:
                st.header("Tekniske Indikatorer")
                add_bollinger = st.checkbox("Legg til Bollinger Bands")
                add_rsi = st.checkbox("Legg til RSI")
                add_macd = st.checkbox("Legg til MACD")

            plot_candlestick_chart_with_indicators(
                st.session_state['stock_data'],
                add_rsi=add_rsi, add_macd=add_macd, add_bollinger=add_bollinger
            )

        # Fundamental analyse
        if 'fundamental_data' in st.session_state:
            with st.sidebar:
                show_fundamental = st.checkbox("Se Fundamental Analyse")

            if show_fundamental:
                display_fundamental_analysis(st.session_state['fundamental_data'])

        # Nyheter
        if 'news_data' in st.session_state:
            st.subheader("Nyheter brukt i analysen")
            display_news_carousel(st.session_state['news_data'])

        # Knapp for AI-analyse
        if 'stock_data' in st.session_state and 'fundamental_data' in st.session_state:
            st.warning("AI-analysen kan ta opp til 1-2 minutter før den blir generert")
            if st.button("Generer AI-Analyse"):
                try:
                    with st.spinner("Genererer AI-analyse..."):
                        combined_analysis = generate_combined_analysis(
                            st.session_state['ticker'],
                            st.session_state['stock_data'],
                            st.session_state['news_data'],
                            st.session_state['fundamental_data'],
                            st.session_state['macro_data'],
                            st.session_state['geopolitical_news'],
                            st.session_state['company_details']
                        )
                        st.session_state['combined_analysis'] = combined_analysis
                        st.success("AI-analysen er klar!")
                except Exception as e:
                    st.error(f"Noe gikk galt under AI-analysen: {e}")

        # Vis AI-analyse
        if 'combined_analysis' in st.session_state:
            st.subheader("AI-basert Helhetlig Analyse")
            st.markdown(st.session_state['combined_analysis'])
            st.markdown("🎯 **Vi vil høre fra deg!** [Fyll ut vårt spørreskjema](https://docs.google.com/forms/d/e/1FAIpQLScwZ3sJaV3fMsuoemdjmrQgGvtwUCMkc1wnS7x1XmfaaVbqZQ/viewform?usp=sharing).")


if __name__ == "__main__":
    main()
