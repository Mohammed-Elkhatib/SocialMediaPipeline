import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from src.models.tweet_model import TweetModel
from src.analytics.processors.word_frequency import WordFrequencyProcessor
from src.analytics.processors.engagement import EngagementProcessor
from src.analytics.exporters.json_exporter import JsonExporter
from src.analytics.exporters.db_exporter import DatabaseExporter

class AnalyticsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize tweet model
        self.tweet_model = TweetModel()
        
        # Initialize processors
        self.word_frequency_processor = WordFrequencyProcessor(self.tweet_model)
        self.engagement_processor = EngagementProcessor(self.tweet_model)
        
        # Initialize exporters
        self.json_exporter = JsonExporter()
        self.db_exporter = DatabaseExporter()
    
    def run_all_analyses(self, time_period: str = "day", platform: Optional[str] = None) -> bool:
        """Run all analytics processors and export results"""
        try:
            self.logger.info(f"Running all analyses for time period: {time_period}, platform: {platform}")
            
            # Calculate date range
            start_date, end_date = self._calculate_date_range(time_period)
            
            # Run word frequency analysis
            word_freq_results = self.word_frequency_processor.process(
                start_date=start_date,
                end_date=end_date,
                platform=platform
            )
            
            # Export word frequency results
            self.json_exporter.export(word_freq_results, "word_frequency")
            self.db_exporter.export(word_freq_results, "word_frequency")
            
            # Run engagement analysis
            engagement_results = self.engagement_processor.process(
                start_date=start_date,
                end_date=end_date,
                platform=platform
            )
            self.json_exporter.export(engagement_results, "engagement")
            self.db_exporter.export(engagement_results, "engagement")
            
            self.logger.info("All analyses completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error running analyses: {str(e)}")
            return False
    
    def _calculate_date_range(self, time_period: str) -> Tuple[datetime.date, datetime.date]:
        """Calculate start and end dates based on time period"""
        end_date = datetime.now().date()
        
        if time_period == "day":
            start_date = end_date - timedelta(days=1)
        elif time_period == "week":
            start_date = end_date - timedelta(weeks=1)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
        elif time_period == "year":
            start_date = end_date - timedelta(days=365)
        else:  # "all"
            # Get earliest post date from database or use a fixed date
            start_date = datetime(2000, 1, 1).date()  # Could be replaced with DB query
        
        return start_date, end_date
        