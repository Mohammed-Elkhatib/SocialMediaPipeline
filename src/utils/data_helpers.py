import re
import uuid
import datetime
import logging
from typing import List, Dict, Any


def generate_unique_id() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def parse_date_string(date_str: str) -> datetime.date:
    """
    Parse a date string into a datetime.date object.

    Args:
        date_str (str): Date string in format 'YYYY-MM-DD'

    Returns:
        datetime.date: Parsed date object
    """
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        # Try alternative formats
        for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date string: {date_str}")


def parse_time_string(time_str: str) -> datetime.time:
    """
    Parse a time string into a datetime.time object.

    Args:
        time_str (str): Time string in format 'HH:MM:SS' or 'HH:MM'

    Returns:
        datetime.time: Parsed time object
    """
    try:
        return datetime.datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        try:
            return datetime.datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            raise ValueError(f"Unable to parse time string: {time_str}")


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace, URLs, and special characters.

    Args:
        text (str): Input text to clean

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_keywords(text: str, min_length: int = 3, stop_words: List[str] = None) -> List[str]:
    """
    Extract keywords from text by removing stop words and short words.

    Args:
        text (str): Input text
        min_length (int): Minimum word length to include
        stop_words (List[str]): List of stop words to exclude

    Returns:
        List[str]: List of keywords
    """
    logger = logging.getLogger(__name__)

    if not text:
        logger.debug("Empty text received, returning empty list")
        return []

    if stop_words is None:
        logger.debug("No stop_words provided, using default Arabic stop words")
        stop_words = {"هذا", "من", "الى", "عن", "إذا", "على", "في", "حتى", "الحين", "الساعة", "اليوم", "هذه", "مع",
                      "هو",
                      "هي", "أن", "بعد", "التفاصيل", "ذلك", "إلى", "ما", "بين", "كل", "لا"}

    # Clean the text
    try:
        cleaned_text = clean_text(text)
        words = cleaned_text.lower().split()
        keywords = [word for word in words if len(word) >= min_length and word not in stop_words]
        logger.debug(f"Extracted {len(keywords)} keywords from text")
        return keywords
    except Exception as e:
        logger.error(f"Error processing text: {e}", exc_info=True)
        return []


def normalize_engagement_counts(count_str: str) -> int:
    """
    Convert engagement count strings like '1.2K' or '4.5M' to integers.

    Args:
        count_str (str): Engagement count string

    Returns:
        int: Normalized count as integer
    """
    if not count_str:
        return 0

    # Strip any non-numeric characters except K, M, or decimal points
    count_str = count_str.strip().upper()

    try:
        # Check if the string is just a number
        return int(float(count_str))
    except ValueError:
        # Handle K, M suffixes
        if 'K' in count_str:
            return int(float(count_str.replace('K', '')) * 1000)
        elif 'M' in count_str:
            return int(float(count_str.replace('M', '')) * 1000000)
        else:
            # Return 0 if we can't parse it
            return 0


def merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries, with values from dict2 taking precedence.

    Args:
        dict1 (Dict[str, Any]): First dictionary
        dict2 (Dict[str, Any]): Second dictionary (with priority)

    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result
