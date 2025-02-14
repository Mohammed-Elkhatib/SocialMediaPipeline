from textblob import TextBlob
import re

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob"""
    blob = TextBlob(text)
    return blob.sentiment.polarity  # Returns a score between -1 and 1

def extract_keywords(text):
    """Extract keywords by removing common words"""
    words = re.findall(r'\b\w+\b', text.lower())  # Tokenization
    stopwords = {"هذا", "من", "الى", "عن", "إذا", "على", "في", "حتى", "الحين", "الساعة", "اليوم", "هذه", "مع","هو", "هي", "أن", "بعد", "التفاصيل", "ذلك", "إلى","ما", "بين", "كل", "لا", "التفاصيل"}# Basic stopwords

    keywords = [word for word in words if word not in stopwords]
    return keywords
