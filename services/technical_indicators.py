import pandas as pd

def generate_technical_analysis(stock_data):
    """
    Genererer en teknisk analyse basert på beregnede indikatorer.
    """
    rsi = stock_data['RSI'].iloc[-1]
    sma = stock_data['SMA'].iloc[-1]
    upper_band = stock_data['Upper'].iloc[-1]
    lower_band = stock_data['Lower'].iloc[-1]
    macd = stock_data['MACD'].iloc[-1]
    signal_line = stock_data['Signal_Line'].iloc[-1]
    
    analysis = f"""
    **Teknisk Analyse:**
    - RSI: {rsi:.2f} ({'Nøytral' if 30 <= rsi <= 70 else 'Overkjøpt' if rsi > 70 else 'Oversolgt'})
    - Bollinger Bands: Aksjen handler nær SMA ({sma:.2f}), med volatilitet mellom {lower_band:.2f} og {upper_band:.2f}.
    - MACD: {'Bullish crossover' if macd > signal_line else 'Bearish crossover'} indikerer {'mulig oppgang' if macd > signal_line else 'mulig nedgang'}.
    """
    return analysis


# Bollinger Bands
def add_bollinger_bands(data, window=20):
    data['SMA'] = data['Close'].rolling(window).mean()
    data['Upper'] = data['SMA'] + 2 * data['Close'].rolling(window).std()
    data['Lower'] = data['SMA'] - 2 * data['Close'].rolling(window).std()
    return data

# RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

# MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    data['MACD'] = short_ema - long_ema
    data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
    return data

# Stochastic Oscillator
def calculate_stochastic(data, window=14):
    data['Lowest_Low'] = data['Low'].rolling(window=window).min()
    data['Highest_High'] = data['High'].rolling(window=window).max()
    data['%K'] = (data['Close'] - data['Lowest_Low']) / (data['Highest_High'] - data['Lowest_Low']) * 100
    data['%D'] = data['%K'].rolling(window=3).mean()
    return data

# EMA/SMA-kryss
def calculate_ema_sma_crossover(data, ema_window=12, sma_window=50):
    data['EMA'] = data['Close'].ewm(span=ema_window, adjust=False).mean()
    data['SMA'] = data['Close'].rolling(window=sma_window).mean()
    data['Crossover'] = data['EMA'] - data['SMA']  # Positivt = bullish, negativt = bearish
    return data

# ADX
def calculate_adx(data, window=14):
    data['+DM'] = data['High'].diff()
    data['-DM'] = data['Low'].diff()
    data['+DM'] = data['+DM'].where((data['+DM'] > data['-DM']) & (data['+DM'] > 0), 0)
    data['-DM'] = data['-DM'].where((data['-DM'] > data['+DM']) & (data['-DM'] > 0), 0)
    data['TR'] = data[['High', 'Low', 'Close']].max(axis=1) - data[['High', 'Low', 'Close']].min(axis=1)
    data['ATR'] = data['TR'].rolling(window=window).mean()
    data['+DI'] = 100 * (data['+DM'] / data['ATR']).rolling(window=window).mean()
    data['-DI'] = 100 * (data['-DM'] / data['ATR']).rolling(window=window).mean()
    data['DX'] = 100 * (abs(data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI']))
    data['ADX'] = data['DX'].rolling(window=window).mean()
    return data
