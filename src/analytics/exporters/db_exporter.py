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
                
            # Extract period information
            period_start = word_freq_data.get('period', {}).get('start')
            period_end = word_freq_data.get('period', {}).get('end')
            
            # Prepare data for database storage
            timestamp = datetime.now().isoformat()
            analysis_id = f"word_freq_{timestamp}"
            
            # Convert the list of word dictionaries to format expected by database
            word_dict = {item['word']: item['count'] for item in word_freq_data['words']}
            
            # Store in database
            self.tweet_model.insert_word_frequencies(
                word_dict, 
                analysis_id=analysis_id,
                period_start=period_start,
                period_end=period_end
            )
            
            # Store metadata about this analysis run
            self.tweet_model.insert_analysis_metadata(
                analysis_id=analysis_id,
                analysis_type='word_frequency',
                parameters=word_freq_data.get('period', {}),
                total_processed=word_freq_data.get('total_processed', 0),
                timestamp=timestamp
            )
            
            logger.info(f"Stored {len(word_freq_data['words'])} word frequencies in database")
            return True
            
        except Exception as e:
            logger.error(f"Error storing word frequencies in database: {str(e)}", exc_info=True)
            return False
        
    def store_hashtag_frequencies(self, word_freq_data: Dict[str, Any]) -> bool:
        """
        Store hashtag frequency data in the database.
        
        Args:
            hashtag_freq_data: Processed hashtag frequency data from HashtagFrequencyProcessor
            
        Returns:
            Boolean indicating success/failure
        """
        try:
            if not word_freq_data.get('words'):
                logger.warning("No word frequency data to store")
                return False
                
            # Extract period information
            period_start = word_freq_data.get('period', {}).get('start')
            period_end = word_freq_data.get('period', {}).get('end')
            
            # Prepare data for database storage
            timestamp = datetime.now().isoformat()
            analysis_id = f"word_freq_{timestamp}"
            
            # Convert the list of word dictionaries to format expected by database
            word_dict = {item['word']: item['count'] for item in word_freq_data['words']}
            
            # Store in database
            self.tweet_model.insert_hashtag_frequencies(
                word_dict, 
                analysis_id=analysis_id,
                period_start=period_start,
                period_end=period_end
            )
            
            # Store metadata about this analysis run
            self.tweet_model.insert_analysis_metadata(
                analysis_id=analysis_id,
                analysis_type='word_frequency',
                parameters=word_freq_data.get('period', {}),
                total_processed=word_freq_data.get('total_processed', 0),
                timestamp=timestamp
            )
            
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
            # Create a unique analysis ID for this run
            timestamp = datetime.now().isoformat()
            analysis_id = f"engagement_{timestamp}"
            
            # Store top likes
            if 'top_likes' in engagement_data:
                likes_data = [
                    {'id': item['id'], 'likes': item['likes']} 
                    for item in engagement_data['top_likes']
                ]
                self.tweet_model.update_top_likes(likes_data, analysis_id=analysis_id)
                
            # Store top comments
            if 'top_comments' in engagement_data:
                comments_data = [
                    {'id': item['id'], 'comments': item['comments']} 
                    for item in engagement_data['top_comments']
                ]
                self.tweet_model.update_top_comments(comments_data, analysis_id=analysis_id)
                
            # Store top retweets
            if 'top_retweets' in engagement_data:
                retweets_data = [
                    {'id': item['id'], 'retweets': item['retweets']} 
                    for item in engagement_data['top_retweets']
                ]
                self.tweet_model.update_top_retweets(retweets_data, analysis_id=analysis_id)
            
            # Store metadata about this analysis run
            self.tweet_model.insert_analysis_metadata(
                analysis_id=analysis_id,
                analysis_type='engagement',
                parameters=engagement_data.get('period', {}),
                total_processed=engagement_data.get('total_processed', 0),
                timestamp=timestamp
            )
            
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
        if analysis_type == 'word_frequency':
            return self.store_word_frequencies(data)
        if analysis_type == 'hashtag_frequency':
            return self.store_hashtag_frequencies(data)
        elif analysis_type == 'engagement':
            return self.store_engagement_data(data)
        else:
            logger.error(f"Unknown analysis type: {analysis_type}")
            return False
