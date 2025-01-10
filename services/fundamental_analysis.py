# services/fundamental_analysis.py
import streamlit as st

def display_fundamental_analysis(ticker):
    # Dummy data for testing (hent fra en API i fremtiden)
    fundamental_data = {
        "P/E Ratio": 25.3,
        "EPS": 5.25,
        "ROE": "18%",
        "Profit Margin": "12.3%"
    }

    st.subheader("Fundamental Analyse")
    st.markdown(f"""
    - **P/E Ratio**: {fundamental_data['P/E Ratio']} (Over markedsnittet, vurder høyt verdsatt)
    - **EPS (Earnings Per Share)**: {fundamental_data['EPS']} (Stabil vekst de siste tre årene)
    - **ROE (Return on Equity)**: {fundamental_data['ROE']} (Indikerer sunn kapitalavkastning)
    - **Profit Margin**: {fundamental_data['Profit Margin']} (God driftseffektivitet)
    """)

    st.bar_chart(pd.DataFrame.from_dict(fundamental_data, orient="index", columns=["Verdi"]))
