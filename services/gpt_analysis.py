import openai
import streamlit as st

# Sett API-nøkkelen for OpenAI
openai_api_key = st.secrets["api_keys"]["openai_key"]
#openai.api_key = "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"
openai.api_key = openai_api_key
def generate_analysis(ticker, stock_data):
    """
    Genererer en AI-basert analyse av aksjen basert på tekniske data.
    """
    recent_data = stock_data.tail(5)  # Bruker siste 5 datapunkter
    prompt = f"""
    Analyser aksjen {ticker} basert på følgende data:
    {recent_data.to_string(index=False)}
    
    Beskriv tekniske signaler og mulige trender og det geopolitiske situasjoner som kan ha en påvirkning på aksjen.
    """
    
    # Oppdatert API-kall for versjon >=1.0.0
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du er en erfaren finansanalytiker."},
            {"role": "user", "content": prompt}
        ]
    )
    print(response)
    analysis_text = response.choices[0].message.content
    return analysis_text.strip()


def generate_combined_analysis(ticker, stock_data, news_data, fundamental_data, macro_data, geopolitical_analysis, company_details):
    # Teknisk analyse
    rsi = stock_data['RSI'].iloc[-1]
    macd = stock_data['MACD'].iloc[-1]
    signal_line = stock_data['Signal_Line'].iloc[-1]
    sma = stock_data['SMA'].iloc[-1]
    upper_band = stock_data['Upper'].iloc[-1]
    lower_band = stock_data['Lower'].iloc[-1]

    technical_analysis = f"""
    Teknisk Analyse:
    - RSI: {rsi:.2f} ({'Nøytral' if 30 <= rsi <= 70 else 'Overkjøpt' if rsi > 70 else 'Oversolgt'})
    - MACD: {'Bullish crossover' if macd > signal_line else 'Bearish crossover'}
    - Bollinger Bands: SMA={sma:.2f}, Øvre Band={upper_band:.2f}, Nedre Band={lower_band:.2f}.
    """

    # Fundamental analyse
    pe_ratio = fundamental_data.get("P/E", "N/A")
    eps = fundamental_data.get("EPS", "N/A")
    roe = fundamental_data.get("ROE", "N/A")
    debt_ratio = fundamental_data.get("Debt Ratio", "N/A")

    fundamental_analysis = f"""
    Fundamental Analyse:
    - P/E Ratio: {pe_ratio} ({'God' if 10 <= pe_ratio <= 20 else 'Medium' if 20 < pe_ratio <= 30 else 'Dårlig'})
    - EPS: {eps} (Høyere er bedre)
    - ROE: {roe}% (Sunn kapitalavkastning)
    - Gjeldsgrad: {debt_ratio} (Lavere er bedre)
    """

    # Nyhetsanalyse
    news_analysis = "Ingen nyheter tilgjengelig." if not news_data else "\n".join(
        [f"- {news['title']}: {news['summary'] or 'Ingen sammendrag tilgjengelig.'}" for news in news_data[:5]]
    )

    # Kombiner data i én prompt
    prompt = f"""
Generer en helhetlig og nybegynnervennlig analyse for aksjen {ticker}. Strukturen må følge punktene nedenfor, og presenteres med klare overskrifter, oppsummeringstabell, kortfattede forklaringer og visuelle høydepunkter (f.eks. emojis og symboler).

---

### 📊 **Oppsummering av Nøkkeltall**  
Gi en oversiktstabell over nøkkeltallene først med tre kolonner: **Indikator**, **Verdi**, og **Vurdering**.

**Eksempel:**
| Indikator        | Verdi       | Vurdering                    |
|------------------|-------------|------------------------------|
| RSI              | {stock_data['RSI'].iloc[-1]:.2f} | 🟢 Oversolgt: Potensiell oppgang   |
| P/E Ratio        | {pe_ratio}  | 🟢 Lav: Underpriset          |
| EPS              | {eps}       | 🟢 Høy: God lønnsomhet       |
| ROE              | {roe}%      | 🔴 Lav: Ineffektiv kapitalbruk |
| Gjeldsgrad       | {fundamental_data.get("Debt Ratio", "N/A")} | 🟡 Moderat risiko              |

---

### 1️⃣ **Teknisk Analyse**
Forklar alle de tekniske indikatorer i kortform med praktiske eksempler. Bruk emojis for visuell klarhet.

- **RSI:** {stock_data['RSI'].iloc[-1]:.2f}  
   📊 *RSI vurderer kjøps- og salgspress.*  
   - **Forklaring:** En verdi over 70 = overkjøpt (fare for nedgang), under 30 = oversolgt (potensiell oppgang).  
   - **Eksempel:** RSI på 88 indikerer at aksjen er overkjøpt og kan falle snart.

- **MACD:** {'Bullish crossover' if stock_data['MACD'].iloc[-1] > stock_data['Signal_Line'].iloc[-1] else 'Bearish crossover'}  
   📈 *MACD viser trendendringer.*  
   - **Forklaring:** En bullish crossover betyr kjøpssignal. En bearish crossover indikerer nedgang.  

- **Bollinger Bands:** SMA={stock_data['SMA'].iloc[-1]:.2f}, Øvre Band={stock_data['Upper'].iloc[-1]:.2f}, Nedre Band={stock_data['Lower'].iloc[-1]:.2f}.  
   📊 *Bollinger Bands vurderer prisnivåer.*  
   - **Eksempel:** Hvis prisen ligger over øvre band på 5012.72, er aksjen overkjøpt.  

---

### 2️⃣ **Fundamental Analyse**
Presenter nøkkeltall med forklaringer og sammenligning med bransjegjennomsnitt:

- **P/E Ratio:** {pe_ratio} 🟢  
   - *P/E viser hvor mye investorer betaler per krone i inntjening.*  
   - **Vurdering:** Lav P/E på {pe_ratio} er positivt sammenlignet med bransjesnittet på 10–20.  

- **EPS (Earnings Per Share):** {eps} 🟢  
   - *Høy EPS betyr at selskapet er lønnsomt.*  

- **ROE:** {roe}% 🔴  
   - *ROE måler hvor effektivt selskapet bruker aksjonærenes kapital.*  
   - **Vurdering:** Lav ROE på {roe}% er under forventet 15–20%.  

- **Gjeldsgrad:** {fundamental_data.get("Debt Ratio", "N/A")} 🟡  
   - *Høy gjeld kan være risikabelt hvis økonomien svekkes.*  

---

### 3️⃣ **Nyheter og Markedssentiment**  
Oppsummer de viktigste nyhetene i punktform:

{news_analysis}

Eksempel:
- **Nyhet:** "Økte oljepriser styrker inntektene til EQNR."  
   - **Konsekvens:** Positive nyheter kan øke investorinteressen.

---

### 4️⃣ **Makroøkonomisk Analyse**  
Analyser makroøkonomiske indikatorer kort:

- **Inflasjon:** {macro_data}% – *Høy inflasjon kan presse kostnadene opp.*  
- **Rente:** {macro_data}% – *Økte renter kan svekke aksjepriser.*  

---

### 5️⃣ **Risikovurdering**  
Oppsummer risikoene tydelig i punkter:

- **Markedsrisiko:** Moderat 🟡 – Volatil oljepris.  
- **Finansiell risiko:** Høy 🔴 – Høy gjeldsgrad.  
- **Makroøkonomisk risiko:** Moderat 🟡 – Inflasjonsutfordringer.  

---

### ✅ **Anbefaling**  
Gi en klar anbefaling:

- **Kortsiktig:** *Hold.* Teknisk analyse viser kortsiktig press.  
- **Langsiktig:** *Kjøp.* Sterk lønnsomhet og stabil posisjon gir langsiktig potensial.

---
(ikke gjenta språk og stil siden din respons skal direkte til en bruker som vil ha informasjon)
**Språk og Stil:**  
- Bruk korte setninger.  
- Forklar fagbegreper enkelt.  
- Unngå repetisjon.  
- Bruk emojis for visuell struktur.
    """

    # Oppdatert API-kall for versjon >=1.0.0
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du er en erfaren finansanalytiker som skriver lettfattelige aksjeanalyser for nybegynnere."},
            {"role": "user", "content": prompt}
        ]
    )
    print(response)
    analysis_text = response.choices[0].message.content
    return analysis_text.strip()
