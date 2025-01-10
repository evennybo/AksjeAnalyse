import plotly.graph_objects as go
import streamlit as st
import plotly.express as px


def styled_box(content, signal_type):
    """
    Viser innhold i en farget, transparent boks basert på signal.
    :param content: Teksten som skal vises.
    :param signal_type: "positive", "neutral", "negative".
    """
    colors = {
        "positive": "rgba(0, 255, 0, 0.1)",  # Grønn
        "neutral": "rgba(255, 255, 0, 0.1)",  # Gul
        "negative": "rgba(255, 0, 0, 0.1)"   # Rød
    }
    box_color = colors.get(signal_type, "rgba(255, 255, 255, 0.1)")  # Default til hvit
    st.markdown(f"""
        <div style="background-color: {box_color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            {content}
        </div>
        """, unsafe_allow_html=True)

def display_technical_indicators_with_boxes(stock_data):
    """
    Viser tekniske indikatorer i fargede bokser basert på signaltyper.
    """
    # **RSI**
    rsi = stock_data['RSI'].iloc[-1]
    rsi_signal = "positive" if 30 <= rsi <= 70 else "negative" if rsi > 70 else "neutral"
    styled_box(
        f"""
        **Relative Strength Index (RSI):**
        - RSI-verdi: {rsi:.2f}
        - {"Overkjøpt (Bearish)" if rsi > 70 else "Oversolgt (Bullish)" if rsi < 30 else "Nøytral"}
        """,
        rsi_signal
    )

    # **Bollinger Bands**
    last_close = stock_data['Close'].iloc[-1]
    upper_band = stock_data['Upper'].iloc[-1]
    lower_band = stock_data['Lower'].iloc[-1]
    bb_signal = (
        "positive" if last_close < upper_band and last_close > lower_band else
        "negative" if last_close > upper_band else "neutral"
    )
    styled_box(
        f"""
        **Bollinger Bands:**
        - Siste sluttkurs: {last_close:.2f}
        - Øvre band: {upper_band:.2f}, Nedre band: {lower_band:.2f}
        - {"Overkjøpt (Bearish)" if last_close > upper_band else "Oversolgt (Bullish)" if last_close < lower_band else "Nøytral"}
        """,
        bb_signal
    )

    # **MACD**
    macd = stock_data['MACD'].iloc[-1]
    signal_line = stock_data['Signal_Line'].iloc[-1]
    macd_signal = "positive" if macd > signal_line else "negative"
    styled_box(
        f"""
        **Moving Average Convergence Divergence (MACD):**
        - MACD-verdi: {macd:.2f}, Signal-linje: {signal_line:.2f}
        - {"Bullish crossover (positiv trend)" if macd > signal_line else "Bearish crossover (negativ trend)"}
        """,
        macd_signal
    )


def display_sector_analysis(sector_data):
    """
    Viser en sammenligning av nøkkeltall for selskapet og konkurrenter.
    """
    st.subheader("📊 Bransjeanalyse")

    # Konverter til DataFrame
    df = pd.DataFrame(sector_data)
    if df.empty:
        st.warning("Ingen bransjedata tilgjengelig.")
        return

    # Plot P/E Ratio
    st.markdown("**P/E Ratio Sammenligning**")
    fig_pe = px.bar(df, x="Ticker", y="P/E Ratio", title="P/E Ratio for Bransjen", color="P/E Ratio")
    st.plotly_chart(fig_pe, use_container_width=True)

    # Plot EPS
    st.markdown("**EPS Sammenligning**")
    fig_eps = px.bar(df, x="Ticker", y="EPS", title="EPS for Bransjen", color="EPS")
    st.plotly_chart(fig_eps, use_container_width=True)

    # Plot ROE
    st.markdown("**ROE Sammenligning**")
    fig_roe = px.bar(df, x="Ticker", y="ROE", title="ROE for Bransjen", color="ROE")
    st.plotly_chart(fig_roe, use_container_width=True)

    # Plot Gjeldsgrad
    st.markdown("**Gjeldsgrad Sammenligning**")
    fig_debt = px.bar(df, x="Ticker", y="Gjeldsgrad", title="Gjeldsgrad for Bransjen", color="Gjeldsgrad")
    st.plotly_chart(fig_debt, use_container_width=True)

def styled_box(content, signal_type):
    """
    Viser innhold i en farget, transparent boks basert på signal.
    :param content: Teksten som skal vises.
    :param signal_type: "positive", "neutral", "negative".
    """
    colors = {
        "positive": "rgba(0, 255, 0, 0.1)",  # Grønn
        "neutral": "rgba(255, 255, 0, 0.1)",  # Gul
        "negative": "rgba(255, 0, 0, 0.1)"   # Rød
    }
    border_colors = {
        "positive": "#00b300",  # Mørkere grønn ramme
        "neutral": "#e6e600",   # Mørkere gul ramme
        "negative": "#e60000"   # Mørkere rød ramme
    }
    box_color = colors.get(signal_type, "rgba(255, 255, 255, 0.1)")  # Default til hvit
    border_color = border_colors[signal_type]
    st.markdown(f"""
        <div style="background-color: {box_color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;  border: 2px solid {border_color};border-radius: 8px; padding: 15px;">
            {content}
        </div>
        """, unsafe_allow_html=True)

def plot_candlestick_chart_with_indicators(
    stock_data, 
    add_rsi=False, 
    add_macd=False, 
    add_bollinger=False
    ):
    # **Candlestick Chart**
    st.subheader("Candlestick Chart med Indikatorer")
    fig = go.Figure()

    # Legg til candlestick-graf
    fig.add_trace(go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'],
        high=stock_data['High'],
        low=stock_data['Low'],
        close=stock_data['Close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name="Candlestick"
    ))

    # Bollinger Bands Forklaring og Fargeboks
    if add_bollinger and 'Upper' in stock_data and 'Lower' in stock_data:
        last_close = stock_data['Close'].iloc[-1]
        upper_band = stock_data['Upper'].iloc[-1]
        lower_band = stock_data['Lower'].iloc[-1]

        signal_type = (
            "negative" if last_close > upper_band else
            "positive" if last_close < lower_band else
            "neutral"
        )
        description = (
             f"<b>Bollinger Bands:</b>  Aksjen handles <b>over det øvre bandet</b> ({upper_band:.2f}), noe som ofte indikerer en **overkjøpt tilstand**. "
            f"Dette skjer når prisen har steget raskt og kan bety at markedet er på vei mot en korreksjon.\n\n"
            f"**Hva betyr dette?** Overkjøpte aksjer kan falle tilbake når investorer tar gevinst." if signal_type == "negative" else
            f"<b>Bollinger Bands:</b> Aksjen handles <b>under det nedre bandet</b> ({lower_band:.2f}), noe som ofte indikerer en **oversolgt tilstand**. "
            f"Dette kan bety at aksjen er undervurdert og kan tiltrekke seg kjøpere.\n\n"
            f"**Hva betyr dette?** Oversolgte aksjer har ofte potensial for en oppgang når kjøpere går inn."if signal_type == "positive" else
            f"<b>Bollinger Bands:</b> Aksjen handles <b>mellom det øvre og nedre bandet</b>, nær SMA "
            f"Dette indikerer normal volatilitet og en balansert pristrend.\n\n"
            f"<b>Hva betyr dette?</b> Det er ingen ekstreme bevegelser som gir kjøps- eller salgssignaler."
        )
        styled_box(description, signal_type)

        # Legg Bollinger Bands til grafen
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['Upper'],
            mode='lines',
            name='Upper Band',
            line=dict(color='blue', dash='dot')
        ))
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['Lower'],
            mode='lines',
            name='Lower Band',
            line=dict(color='blue', dash='dot')
        ))
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['SMA'],
            mode='lines',
            name='SMA (20)',
            line=dict(color='orange')
        ))

    # Oppdater hovedgrafen først
    fig.update_layout(
        title="Candlestick Chart ",
        xaxis_title="Dato",
        yaxis_title="Pris",
        template="plotly_white",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    # RSI Forklaring og Fargeboks
    if add_rsi and 'RSI' in stock_data:
        last_rsi = stock_data['RSI'].iloc[-1]
        signal_type = (
            "positive" if last_rsi < 30 else
            "negative" if last_rsi > 70 else
            "neutral"
        )
        description = (
            f"<b>RSI:</b> Verdien er <b>{last_rsi:.2f}</b>, noe som betyr at aksjen er <b>oversolgt</b>. Dette kan indikere en kjøpsmulighet "
            f"fordi prisen kan være for lav i forhold til aksjens reelle verdi.\n\n<b>Hva betyr dette?</b> Investorer vurderer ofte å kjøpe i slike situasjoner." if signal_type == "positive" else
            f"<b>RSI:</b> Verdien er <b>{last_rsi:.2f}</b>, noe som betyr at aksjen er <b>overkjøpt</b>. Dette kan indikere en mulig nedgang "
            f"fordi prisen kan ha steget for mye på kort tid.\n\n<b>Hva betyr dette?</b> Investorer kan vurdere å selge eller ta gevinst." if signal_type == "negative" else
            f"<b>RSI:</b> Verdien er <b>{last_rsi:.2f}</b>, noe som betyr at markedet er balansert.\n\n<b>Hva betyr dette?</b> Det er ingen sterke kjøps- eller salgssignaler."
        )
        styled_box(description, signal_type)

        # Legg RSI til grafen
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple')
        ))
        # Horisontale linjer for overkjøpt/oversolgt
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overkjøpt (70)")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversolgt (30)")

        fig_rsi.update_layout(
            title="Relative Strength Index (RSI)",
            xaxis_title="Dato",
            yaxis_title="RSI",
            yaxis=dict(range=[0, 100]),
            template="plotly_white",
            height=300
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

    # MACD Forklaring og Fargeboks
    if add_macd and 'MACD' in stock_data and 'Signal_Line' in stock_data:
        last_macd = stock_data['MACD'].iloc[-1]
        last_signal = stock_data['Signal_Line'].iloc[-1]
        signal_type = (
            "positive" if last_macd > last_signal else
            "negative"
        )
        description = (
            f"<b>MACD:</b> Verdien er <b>{last_macd:.2f}</b> og har krysset <b>over</b> signal-linjen. Dette indikerer en <b>bullish trend</b> "
            f"og mulighet for videre oppgang.\n\n<b>Hva betyr dette?</b> Mange investorer ser dette som et kjøpssignal." if signal_type == "positive" else
            f"<b>MACD:</b> Verdien er <b>{last_macd:.2f}</b> og har krysset <b>under</b> signal-linjen. Dette indikerer en <b>bearish trend</b> "
            f"og mulig nedgang.\n\n<b>Hva betyr dette?</b> Investorer kan vurdere å selge eller unngå å kjøpe i slike situasjoner."
        )
        styled_box(description, signal_type)

        # Legg MACD til grafen
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue')
        ))
        fig_macd.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['Signal_Line'],
            mode='lines',
            name='Signal Line',
            line=dict(color='red', dash='dot')
        ))
        fig_macd.update_layout(
            title="Moving Average Convergence Divergence (MACD)",
            xaxis_title="Dato",
            yaxis_title="MACD",
            template="plotly_white",
            height=300
        )
        st.plotly_chart(fig_macd, use_container_width=True)

def display_news_carousel(news_data):
    """
    Viser nyhetsartikler som en karusell med en grå transparent bakgrunn og tykkere kant.
    """
    st.subheader("Nyhetskarusell")
    current_index = st.session_state.get("news_index", 0)

    # CSS-stil for grå bakgrunn og tykk kant
    news_box_style = """
        <style>
            .news-box {
                background-color: rgba(200, 200, 200, 0.2); /* Lys transparent grå */
                border: 2px solid rgba(100, 100, 100, 0.8); /* Tykk mørkegrå kant */
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            }
        </style>
    """
    st.markdown(news_box_style, unsafe_allow_html=True)

    if news_data:
        # Navigasjonsknapper
        col1, col2 = st.columns([1, 1])
        with col1:
            if current_index > 0:
                if st.button("Forrige"):
                    st.session_state.news_index -= 1

        with col2:
            if current_index < len(news_data) - 1:
                if st.button("Neste"):
                    st.session_state.news_index += 1

        # Vis valgt nyhet med grå bakgrunn og tykk kant
        news = news_data[current_index]
        st.markdown(f"""
        <div class="news-box">
            <h3><a href="{news['link']}" target="_blank" text-decoration: none;">{news['title']}</a></h3>
            <p><em>Publisert av: {news.get('publisher', 'Ukjent')} - {news.get('date', 'Ukjent')}</em></p>
            <p>{news.get('summary', 'Ingen sammendrag tilgjengelig.')}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Ingen nyheter tilgjengelig.")

def styled_box_fundamental(name, value, description, explanation, signal_type):
    """
    Viser innhold i en farget, transparent boks basert på signal, med forbedret styling.
    """
    colors = {
        "positive": "rgba(0, 255, 0, 0.1)",  # Lys grønn bakgrunn
        "neutral": "rgba(255, 255, 0, 0.1)",  # Lys gul bakgrunn
        "negative": "rgba(255, 0, 0, 0.1)"   # Lys rød bakgrunn
    }
    border_colors = {
        "positive": "#00b300",  # Mørkere grønn ramme
        "neutral": "#e6e600",   # Mørkere gul ramme
        "negative": "#e60000"   # Mørkere rød ramme
    }
    box_color = colors.get(signal_type, "rgba(255, 255, 255, 0.1)")
    border_color = border_colors.get(signal_type, "#cccccc")

    # Render boksen med ren HTML
    st.markdown(f"""
        <div style="
            background-color: {box_color};
            border: 2px solid {border_color};
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            color: inherit;
            font-size: 16px;
            line-height: 1.5;
        ">
            <p><b>{name}:</b> {value}</p>
            <p>{description}</p>
            <p><b>Vurdering:</b> {explanation}</p>
        </div>
        """, unsafe_allow_html=True)


def display_fundamental_analysis(fundamental_data):
    """
    Viser fundamental analyse med detaljerte beskrivelser av hva tallene betyr.
    """
    st.subheader("📊 Fundamental Analyse")

    def determine_color_and_message(name, value, low_threshold, high_threshold):
        try:
            value = float(str(value).replace('%', '').replace(',', ''))
            if name == "P/E Ratio":
                if value < low_threshold:
                    return "positive", "Lav verdi: Aksjen kan være undervurdert sammenlignet med inntjeningen."
                elif low_threshold <= value <= high_threshold:
                    return "neutral", "Sunn verdi: Aksjen handles til en rimelig pris."
                else:
                    return "negative", "Høy verdi: Aksjen kan være overpriset sammenlignet med inntjeningen."

            elif name == "ROE":
                if value < low_threshold:
                    return "negative", "Lav verdi: Selskapet gir svak avkastning på egenkapitalen."
                elif value > high_threshold:
                    return "positive", "Høy verdi: Selskapet gir sterk avkastning på egenkapitalen."
                else:
                    return "neutral", "Moderat verdi: Akseptabel avkastning på egenkapitalen."

            else:  # For EPS og Gjeldsgrad
                if value < low_threshold:
                    return "negative", "Lav verdi: Potensiell risiko."
                elif value > high_threshold:
                    return "positive", "Høy verdi: Sterk indikasjon."
                else:
                    return "neutral", "Moderat verdi: Balansert situasjon."
        except ValueError:
            return "neutral", "Ingen data tilgjengelig."

    # Indikatorer med tilhørende terskler og beskrivelser
    indicators = [
        {"name": "P/E Ratio", "value": fundamental_data.get("P/E", "N/A"), "low": 10, "high": 20,
         "description": "P/E Ratio måler hvor mye investorer betaler per krone selskapet tjener."},
        {"name": "EPS (Earnings Per Share)", "value": fundamental_data.get("EPS", "N/A"), "low": 1, "high": 5,
         "description": "EPS viser selskapets inntjening per aksje. Høy EPS er et tegn på lønnsomhet."},
        {"name": "ROE (Return on Equity)", "value": f"{fundamental_data.get('ROE', 'N/A')}%", "low": 10, "high": 15,
         "description": "ROE måler selskapets avkastning på egenkapital. En ROE over 15% anses som svært god."},
        {"name": "Gjeldsgrad", "value": fundamental_data.get("Debt Ratio", "N/A"), "low": 0, "high": 100,
         "description": "Gjeldsgraden viser selskapets gjeld i forhold til egenkapital. Høy gjeldsgrad kan være risikabelt."}
    ]

    # Loop gjennom indikatorene og vis dem
    for indicator in indicators:
        signal, explanation = determine_color_and_message(
            indicator["name"], indicator["value"], indicator["low"], indicator["high"]
        )

        # Send navn, verdi, beskrivelse og vurdering til styled_box_fundamental
        styled_box_fundamental(
            name=indicator["name"],
            value=indicator["value"],
            description=indicator["description"],
            explanation=explanation,
            signal_type=signal
        )



def display_macro_analysis(macro_data):
    st.subheader("Makroøkonomisk Analyse")
    st.write(f"""
    - **BNP Vekst**: {macro_data['bnp_growth']}% (Høyere vekst er positivt for aksjemarkedet)
    - **Inflasjonsrate**: {macro_data['inflation_rate']}% (Høy inflasjon kan redusere kjøpekraften)
    - **Rente**: {macro_data['interest_rate']}% (Høye renter kan øke finansieringskostnader)
    - **Arbeidsledighet**: {macro_data['unemployment_rate']}% (Lav arbeidsledighet støtter økonomisk vekst)
    """)


def display_geopolitical_analysis(geopolitical_news):
    st.subheader("Geopolitisk Analyse")

    st.write("### Landsspesifikke Nyheter")
    for news in geopolitical_news['country_news'][:5]:
        st.markdown(f"- **{news['title']}**: {news['description'] or 'Ingen sammendrag tilgjengelig.'}")

    st.write("### Industrinyheter")
    for news in geopolitical_news['industry_news'][:5]:
        st.markdown(f"- **{news['title']}**: {news['description'] or 'Ingen sammendrag tilgjengelig.'}")

    st.write("### Globale Nyheter")
    for news in geopolitical_news['global_news'][:5]:
        st.markdown(f"- **{news['title']}**: {news['description'] or 'Ingen sammendrag tilgjengelig.'}")


