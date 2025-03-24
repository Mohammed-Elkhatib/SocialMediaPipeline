import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from collections import Counter

from src.models.relational.tweets import TweetModel
from src.utils.data_helpers import extract_keywords

logger = logging.getLogger(__name__)


class WordFrequencyProcessor:
    """
    Processes tweet content to analyze word frequencies.
    
    This processor extracts keywords from tweets, calculates frequencies,
    identifies trends, and prepares data for exporters.
    """

    def __init__(self):
        """Initialize the word frequency processor."""
        self.tweet_model = TweetModel()
        logger.info("Word frequency processor initialized")

    def process(self,
                start_date: Optional[date] = None,
                end_date: Optional[date] = None,
                platform: str = 'x',
                top_n: int = 20,
                min_word_length: int = 2,
                exclude_words: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process tweets to extract word frequency data.
        
        Args:
            start_date: Start date for tweet filtering (None for no start limit)
            end_date: End date for tweet filtering (None for no end limit)
            platform: Platform identifier (e.g., 'x' for Twitter)
            top_n: Number of top words to return
            min_word_length: Minimum length for words to be counted
            exclude_words: List of words to exclude from analysis
            
        Returns:
            Dictionary with word frequency data and metadata
        """
        exclude_words = exclude_words or []

        # Log the processing request
        date_range = f"from {start_date} to {end_date}" if start_date and end_date else "all time"
        logger.info(f"Processing word frequencies for {platform} {date_range}")

        try:
            # Fetch tweets from database using date range
            tweets = self.tweet_model.fetch_posts(
                platform=platform,
                start_date=start_date,
                end_date=end_date
            )
            
            if not tweets:
                logger.warning(f"No tweets found for {platform} {date_range}")
                return {"words": [], "total_processed": 0, "status": "no_data"}

            # Process the tweets
            word_counts = self._count_words(
                tweets=tweets,
                exclude_words=exclude_words
            )

            # Get the top N words
            top_words = self._get_top_words(word_counts, top_n)

            # Calculate trending words (words with significant recent growth)
            # This would compare to previous periods if implemented
            trending = self._get_trending_words(word_counts, top_n=20)

            # Create result object
            result = {
                "words": [{"word": word, "count": count} for word, count in top_words],
                "trending": [{"word": word, "growth": growth} for word, growth in trending],
                "total_words": sum(word_counts.values()),
                "unique_words": len(word_counts),
                "total_processed": len(tweets),
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Word frequency processing completed: {len(tweets)} tweets analyzed")
            return result

        except Exception as e:
            logger.error(f"Error processing word frequencies: {str(e)}", exc_info=True)
            return {
                "words": [],
                "total_processed": 0,
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    def _count_words(tweets: List[Dict], exclude_words: List[str] = None) -> Counter:
        """
        Count word frequencies across all tweet content.
        
        Args:
            tweets: List of tweet dictionaries from the database
            
        Returns:
            Counter object with word frequencies
        """
        word_counter = Counter()

        for tweet in tweets:
            content = tweet.get('content')
            if content:
                # Extract keywords from tweet content
                keywords = extract_keywords(content, stop_words=exclude_words)
                # Update counter
                word_counter.update(keywords)

        return word_counter

    def _get_top_words(self, word_counts: Counter, top_n: int) -> List[tuple]:
        """
        Get the top N words by frequency.
        
        Args:
            word_counts: Counter object with word frequencies
            top_n: Number of top words to return
            
        Returns:
            List of (word, count) tuples for top words
        """
        return word_counts.most_common(top_n)

    def _get_trending_words(self,
                            current_counts: Counter,
                            top_n: int = 20,
                            previous_counts: Optional[Counter] = None) -> List[tuple]:
        """
        Identify trending words based on growth in frequency.
        
        In a real implementation, this would compare to historical data.
        For now, it just returns the top words as a placeholder.
        
        Args:
            current_counts: Current word frequency counts
            top_n: Number of trending words to return
            previous_counts: Previous period word counts (not implemented yet)
            
        Returns:
            List of (word, growth_rate) tuples for trending words
        """
        # In a full implementation, we would:
        # 1. Fetch previous period data from database
        # 2. Calculate growth rate for each word
        # 3. Sort by growth rate and return top N

        # For now, just return the top words with a placeholder growth value
        trending = []
        for word, count in current_counts.most_common(top_n):
            # Placeholder: 1.0 means "unchanged"
            trending.append((word, 1.0))

        return trending

    def analyze_by_time_periods(self,
                                period_type: str = 'day',
                                num_periods: int = 7,
                                platform: str = 'x',
                                top_n: int = 20) -> Dict[str, Any]:
        """
        Analyze word frequencies across multiple time periods.
        
        Args:
            period_type: Type of period ('day', 'week', 'month')
            num_periods: Number of periods to analyze
            platform: Platform identifier
            top_n: Number of top words per period
            
        Returns:
            Dictionary with time-segmented word frequency data
        """
        # This would be implemented to show trends over time
        # For brevity, we'll just add the method signature for now

        # 1. Determine date ranges for each period
        # 2. Process each period separately
        # 3. Combine results into a time series

        # Placeholder return
        return {"status": "not_implemented", "message": "Time period analysis not yet implemented"}
