# services/geopolitical_analysis.py
from services.gpt_analysis import generate_analysis

def generate_geopolitical_analysis(news_data):
    if news_data:
        news_summary = ". ".join([news["summary"] for news in news_data if news["summary"]])
        prompt = f"""
        Basert på følgende nyhetsdata, analyser de geopolitiske og sektorspesifikke risikoene og mulighetene for selskapet:
        {news_summary}
        """
        return generate_analysis(prompt)
    return "Ingen geopolitiske analyser tilgjengelig basert på nyhetsdata."
