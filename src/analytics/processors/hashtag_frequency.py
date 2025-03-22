import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from collections import Counter
import re

from src.models.relational.tweets import TweetModel  # Assuming PostModel fetches posts from your database

logger = logging.getLogger(__name__)

class HashtagFrequencyProcessor:
    """
    Processes post content to analyze hashtag frequencies.
    
    This processor extracts hashtags from posts, calculates frequencies,
    and prepares data for exporters.
    """
    
    def __init__(self):
        """Initialize the hashtag frequency processor."""
        self.post_model = TweetModel()
        logger.info("Hashtag frequency processor initialized")
    
    def process(self, 
               start_date: Optional[date] = None,
               end_date: Optional[date] = None,
               platform: str = 'x',
               top_n: int = 100,
               exclude_hashtags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process posts to extract hashtag frequency data.
        
        Args:
            start_date: Start date for post filtering (None for no start limit)
            end_date: End date for post filtering (None for no end limit)
            platform: Platform identifier (e.g., 'x' for Twitter)
            top_n: Number of top hashtags to return
            exclude_hashtags: List of hashtags to exclude from analysis
            
        Returns:
            Dictionary with hashtag frequency data and metadata
        """
        exclude_hashtags = exclude_hashtags or []
        
        # Log the processing request
        date_range = f"from {start_date} to {end_date}" if start_date and end_date else "all time"
        logger.info(f"Processing hashtag frequencies for {platform} {date_range}")
        
        try:
            # Fetch posts from database using date range
            posts = self.post_model.fetch_posts(
                platform=platform,
                start_date=start_date,
                end_date=end_date
            )
            
            if not posts:
                logger.warning(f"No posts found for {platform} {date_range}")
                return {"hashtags": [], "total_processed": 0, "status": "no_data"}
            
            # Process the posts
            hashtag_counts = self._count_hashtags(
                posts=posts,
                exclude_hashtags=exclude_hashtags
            )
            
            # Get the top N hashtags
            top_hashtags = self._get_top_hashtags(hashtag_counts, top_n)
            
            # Create result object
            result = {
                "hashtags": [{"hashtag": hashtag, "count": count} for hashtag, count in top_hashtags],
                "total_hashtags": sum(hashtag_counts.values()),
                "unique_hashtags": len(hashtag_counts),
                "total_processed": len(posts),
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Hashtag frequency processing completed: {len(posts)} posts analyzed")
            return result
            
        except Exception as e:
            logger.error(f"Error processing hashtag frequencies: {str(e)}", exc_info=True)
            return {
                "hashtags": [],
                "total_processed": 0,
                "status": "error",
                "error": str(e)
            }
    
    def _count_hashtags(self, 
                        posts: List[Dict], 
                        exclude_hashtags: List[str] = None) -> Counter:
        """
        Count hashtag frequencies across all post content.
        
        Args:
            posts: List of post dictionaries from the database
            exclude_hashtags: List of hashtags to exclude
            
        Returns:
            Counter object with hashtag frequencies
        """
        exclude_hashtags = set(h.lower() for h in (exclude_hashtags or []))
        hashtag_counter = Counter()
        
        for post in posts:
            content = post.get('content')
            if content:
                # Extract hashtags using regex
                hashtags = re.findall(r'#\w+', content)
                
                # Filter hashtags by exclusion list
                filtered_hashtags = [
                    hashtag.lower() for hashtag in hashtags if hashtag.lower() not in exclude_hashtags
                ]
                
                # Update counter
                hashtag_counter.update(filtered_hashtags)
        
        return hashtag_counter
    
    def _get_top_hashtags(self, hashtag_counts: Counter, top_n: int) -> List[tuple]:
        """
        Get the top N hashtags by frequency.
        
        Args:
            hashtag_counts: Counter object with hashtag frequencies
            top_n: Number of top hashtags to return
            
        Returns:
            List of (hashtag, count) tuples for top hashtags
        """
        return hashtag_counts.most_common(top_n)
