def format_currency(value):
    """
    Formaterer tall til valutaformat.
    """
    return f"{value:,.2f} NOK"

def handle_error(e):
    """
    Logger feil og returnerer en brukerlesbar melding.
    """
    print(f"Feil: {e}")
    return "Noe gikk galt. Vennligst prøv igjen."

def calculate_key_metrics(stock_data):
    avg_price = stock_data['Close'].mean()
    high_price = stock_data['High'].max()
    low_price = stock_data['Low'].min()
    return avg_price, high_price, low_price

