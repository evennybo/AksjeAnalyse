import yfinance as yf
import pandas as pd
import requests
import tradingeconomics as te
import streamlit as st

def get_company_suggestions(query):
    try:
        # Bruk Yahoo Finance til å søke etter tickere
        data = yf.Ticker(query)
        if data.info:  # Hvis informasjon om selskapet finnes
            return [data.info.get("shortName", ""), query]
    except Exception as e:
        print(f"Feil under henting av forslag: {e}")
    return []

def get_usd_to_nok_rate():
    """
    Henter dagens valutakurs for USD til NOK fra Yahoo Finance.
    """
    try:
        exchange_rate = yf.Ticker("USDNOK=X")
        rate = exchange_rate.history(period="1d")['Close'].iloc[-1]
        return rate
    except Exception as e:
        print(f"Kunne ikke hente USD/NOK valutakurs: {e}")
        return None

def fetch_stock_data(ticker, period="1y", interval="1d"):
    """
    Henter aksjedata og fundamentaldata for et gitt ticker-symbol,
    og konverterer priser til NOK uten å forstyrre prosentbaserte verdier.
    """
    stock = yf.Ticker(ticker)

    # Hent prisdata
    data = stock.history(period, interval)
    if data.empty:
        raise ValueError("Fant ingen data for det angitte symbolet.")
    
    # Hent valutakurs for USD/NOK
    usd_to_nok = get_usd_to_nok_rate()
    if not usd_to_nok:
        print("Kunne ikke hente valutakurs. Returnerer data i USD.")
        return data, stock.info

    # Konverter prisdata til NOK
    data['Open'] *= usd_to_nok
    data['High'] *= usd_to_nok
    data['Low'] *= usd_to_nok
    data['Close'] *= usd_to_nok

    # Hent fundamentaldata uten å forstyrre prosentbaserte verdier
    fundamental_data = {
        "P/E": stock.info.get("forwardPE", "N/A"),
        "EPS": stock.info.get("trailingEps", "N/A"),
        "ROE": stock.info.get("returnOnEquity", "N/A"),  # Prosent - skal ikke konverteres
        "Debt Ratio": stock.info.get("debtToEquity", "N/A")  # Prosent eller ratio - ikke konverteres
    }

    # Konverter kun EPS til NOK
    if fundamental_data["EPS"] != "N/A" and isinstance(fundamental_data["EPS"], (int, float)):
        fundamental_data["EPS"] = round(fundamental_data["EPS"] * usd_to_nok, 2)

    print("Fundamentaldata i NOK:", fundamental_data)
    return data, fundamental_data

def fetch_news(ticker):
    API_KEY = st.secrets["api_keys"]["newsdata_key"]
    """
    Henter nyheter relatert til en gitt ticker fra newsdata.io.
    """
    try:
        BASE_URL = "https://newsdata.io/api/1/latest"

        # Sett opp parametrene for forespørselen
        params = {
            "apikey": API_KEY,
            "q": ticker,
            "language": "en"  # Filtrer på engelsk for relevans
        }

        # Send forespørsel
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Kaster en feil hvis statusen ikke er 200

        # Parse JSON-responsen
        data = response.json()
        if data.get("status") == "success" and "results" in data:
            return [
                {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "publisher": item.get("source_id"),
                    "summary": item.get("description"),
                    "date": item.get("pubDate")
                }
                for item in data["results"]
            ]
        else:
            print("Ingen relevante nyheter funnet i API-responsen.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Feil ved forespørsel til newsdata.io: {e}")
        return []

def check_data_recency(stock_data):
    """
    Sjekker om aksjedataen er oppdatert.
    """
    try:
        last_date = stock_data.index[-1]
        today = pd.Timestamp.now().date()
        if last_date.date() == today:
            return "Data er oppdatert."
        else:
            return f"Dataen er fra {last_date.date()}. Sørg for at du bruker en oppdatert datakilde."
    except Exception as e:
        print(f"Error checking data recency: {e}")
        return "Ukjent oppdateringsstatus."

def fetch_fundamental_data(ticker):
    """
    Henter fundamentale data som P/E, EPS, ROE osv.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    fundamental_data = {
        "P/E": info.get("forwardPE"),
        "EPS": info.get("trailingEps"),
        "ROE": info.get("returnOnEquity") * 100 if info.get("returnOnEquity") else None,
        "Debt Ratio": info.get("debtToEquity"),
    }
    return fundamental_data



def fetch_macro_data_combined(country):
    """
    Henter makroøkonomiske data for et gitt land fra både World Bank API og Trading Economics API.
    """
    
    api_key = st.secrets["api_keys"]["tradingeconomics_key"]
    # API URL
    world_bank_url = f"https://api.tradingeconomics.com/worldbank/country/{country}?c={api_key}"

    # Nøkkelindikatorer som skal filtreres
    important_indicators = [
        "gdp_", "gdp_per_capita_", "gdp_per_capita_growth_(annual_%)",
        "inflation,_consumer_prices_(annual_%)", "trade_(%_of_gdp)",
        "tax_revenue_(%_of_gdp)", "current_account_balance_(%_of_gdp)",
        "population,_total", "population_growth_(annual_%)",
        "urban_population_(%_of_total)", "access_to_electricity_(%_of_population)",
        "individuals_using_the_internet_(%_of_population)",
        "employment_to_population_ratio,_15+,_total_", "unemployment,_total_",
        "foreign_direct_investment,_net_inflows_(%_of_gdp)",
        "domestic_credit_to_private_sector_(%_of_gdp)", "financial_system_deposits_to_gdp_"
    ]

    # Initialiser filtrert data
    macro_data = {
        "country": country,
        "world_bank_data": {}
    }

    # Hent data fra World Bank API
    try:
        wb_response = requests.get(world_bank_url)
        if wb_response.status_code == 200:
            wb_data = wb_response.json()  # Antatt liste med data
            # Sjekk om wb_data er en liste
            if isinstance(wb_data, list):
                for item in wb_data:
                    key = item.get("title", "unknown").lower().replace(" ", "_")
                    value = item.get("last", "N/A")
                    # Sjekk om nøkkel matcher noen av de viktige indikatorene
                    if any(indicator in key for indicator in important_indicators):
                        # Konverter prosent eller tall fra string til float
                        try:
                            if isinstance(value, str) and "%" in value:
                                value = float(value.replace("%", "")) / 100  # Prosent til desimal
                            elif isinstance(value, str):
                                value = float(value)
                        except ValueError:
                            pass  # Hvis konvertering feiler, behold verdien som den er
                        macro_data["world_bank_data"][key] = value
            else:
                print("Uventet format for World Bank API-data")
        else:
            print(f"Feil ved henting av data fra World Bank API: {wb_response.status_code}")
    except Exception as e:
        print(f"Feil under kall til World Bank API: {e}")

    return macro_data

# Hent makroøkonomiske indikatorer for et spesifikt land
def fetch_trading_economics_data(country):
    # Autentisering med API-nøkkel

    api_key = st.secrets["api_keys"]["tradingeconomics_key"]
    te.login(api_key)
    try:
        # Hent data basert på land
        data = te.getIndicatorData(country=country)
        print("DATA FROM FINACIALS", data)
        # Filtrer de viktigste indikatorene
        important_data = [
            { 
                "category": item.get("Category", "N/A"),
                "event": item.get("Event", "N/A"),
                "actual": item.get("Actual", "N/A"),
                "previous": item.get("Previous", "N/A"),
                "forecast": item.get("Forecast", "N/A"),
                "date": item.get("Date", "N/A")
            }
            for item in data if item.get("Importance", "N/A") == "3"  # Henter viktige indikatorer
        ]
        return important_data
    except Exception as e:
        print(f"Feil ved henting av data: {e}")
        return []


def fetch_macro_data(country):
    try:
        # Første forsøk: Bruk World Bank
        macro_data = fetch_macro_data_via_worldbank(country)
        if macro_data:
            return macro_data
    except Exception as e:
        print("Feil i World Bank API:", e)

    # Fallback til FRED API for detaljerte statsøkonomiske data
    try:
        api_key = st.secrets["api_keys"]["tradingeconomics_key"]
        url = f"https://api.tradingeconomics.com/fred/states?c={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            fred_data = response.json()
            return {
                "country": country,
                "bnp_growth": fred_data.get("BNP Growth", "N/A"),
                "interest_rate": fred_data.get("Interest Rate", "N/A"),
                "inflation_rate": fred_data.get("Inflation Rate", "N/A"),
                "unemployment_rate": fred_data.get("Unemployment Rate", "N/A")
            }
    except Exception as e:
        print("Feil i FRED API:", e)

    return {
        "country": country,
        "bnp_growth": "N/A",
        "interest_rate": "N/A",
        "inflation_rate": "N/A",
        "unemployment_rate": "N/A"
    }


def fetch_geopolitical_news(region):
    """
    Henter nyheter relatert til en spesifikk region.
    """
    api_url = "https://newsdata.io/api/1/news"
    api_key = st.secrets["api_keys"]["newsdata_key"]
    params = {
        "apikey": api_key,
        "q": region,
        "language": "en"
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print("GEOPOLITICAL NEWS NOT RECIVED")
        return []


def fetch_company_details(ticker):
    """
    Henter landkode og industri/sektor for selskapet via yfinance.
    """
    stock = yf.Ticker(ticker)
    company_info = stock.info

    name =  company_info.get("longName", "N/A")
    country = company_info.get("country", "N/A")
    industry = company_info.get("industry", "N/A")
    sector = company_info.get("sector", "N/A")

    return {
        "country": country,
        "industry": industry,
        "sector": sector,
        "name": name
    }

def fetch_combined_geopolitical_news(company_details):
    country_news = fetch_geopolitical_news(company_details['country'])
    industry_news = fetch_geopolitical_news(company_details['industry'])
    global_news = fetch_geopolitical_news("global")
    
    return {
        "country_news": country_news,
        "industry_news": industry_news,
        "global_news": global_news
    }


