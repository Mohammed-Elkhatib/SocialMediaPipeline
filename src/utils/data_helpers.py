import re


def extract_keywords(text):
    """Extract keywords by removing common words"""
    words = re.findall(r'\b\w+\b', text.lower())  # Tokenization
    stopwords = {"هذا", "من", "الى", "عن", "إذا", "على", "في", "حتى", "الحين", "الساعة", "اليوم", "هذه", "مع", "هو", "هي", "أن", "بعد", "التفاصيل", "ذلك", "إلى", "ما", "بين", "كل", "لا"}  # Basic stopwords
    keywords = [word for word in words if word not in stopwords]
    return keywords
