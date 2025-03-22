import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.relational.tweets import TweetModel

logger = logging.getLogger(__name__)


class DbExporter:
    """
    Exports analytics results to the database.
    
    This class handles formatting analytics results for database storage
    and calls the appropriate database model methods.
    """
    
    def __init__(self):
        """Initialize the database exporter."""
        self.tweet_model = TweetModel()
        logger.info("Database exporter initialized")

    def store_word_frequencies(self, word_freq_data: Dict[str, Any]) -> bool:
        """
        Store word frequency data in the database.

        Args:
            word_freq_data: Processed word frequency data from WordFrequencyProcessor

        Returns:
            Boolean indicating success/failure
        """
        try:
            if not word_freq_data.get('words'):
                logger.warning("No word frequency data to store")
                return False

            # Convert the list of word dictionaries to format expected by database
            word_dict = {item['word']: item['count'] for item in word_freq_data['words']}

            # Store in database using the existing method
            self.tweet_model.insert_word_frequencies(word_dict)

            logger.info(f"Stored {len(word_freq_data['words'])} word frequencies in database")
            return True

        except Exception as e:
            logger.error(f"Error storing word frequencies in database: {str(e)}", exc_info=True)
            return False

    def store_engagement_data(self, engagement_data: Dict[str, Any]) -> bool:
        """
        Store engagement data in the database.

        Args:
            engagement_data: Processed engagement data from EngagementProcessor

        Returns:
            Boolean indicating success/failure
        """
        try:
            # Store top likes
            if 'top_posts' in engagement_data:
                top_posts = engagement_data['top_posts']

                # Extract top likes if available
                likes_data = [
                    {'id': post['id'], 'likes': post['likes']}
                    for post in top_posts
                ]
                if likes_data:
                    self.tweet_model.update_top_likes(likes_data)
                    logger.info(f"Stored {len(likes_data)} top liked posts")

                # Extract top comments if available
                comments_data = [
                    {'id': post['id'], 'comments': post['comments']}
                    for post in top_posts
                ]
                if comments_data:
                    self.tweet_model.update_top_comments(comments_data)
                    logger.info(f"Stored {len(comments_data)} top commented posts")

                # Extract top retweets if available
                retweets_data = [
                    {'id': post['id'], 'retweets': post['retweets']}
                    for post in top_posts
                ]
                if retweets_data:
                    self.tweet_model.update_top_retweets(retweets_data)
                    logger.info(f"Stored {len(retweets_data)} top retweeted posts")

            logger.info("Engagement data stored in database")
            return True

        except Exception as e:
            logger.error(f"Error storing engagement data in database: {str(e)}", exc_info=True)
            return False

    def store_analysis_results(self, analysis_type: str, data: Dict[str, Any]) -> bool:
        """
        General method to store any type of analysis results.

        Args:
            analysis_type: Type of analysis ('word_frequency', 'engagement', etc.)
            data: Processed analysis data

        Returns:
            Boolean indicating success/failure
        """
        # Map of analysis types to their handler methods
        handlers = {
            'word_frequency': self.store_word_frequencies,
            'engagement': self.store_engagement_data,
            # Add more handlers as needed
        }

        if analysis_type in handlers:
            return handlers[analysis_type](data)
        else:
            logger.error(f"Unknown analysis type: {analysis_type}")
            return False
