import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JsonExporter:
    """
    Exports analytics results to JSON files for dashboard consumption.

    This class handles formatting analytics results for the dashboard
    and saves them to the appropriate JSON files.
    """

    def __init__(self, data_folder: Optional[str] = None):
        """
        Initialize the JSON exporter.

        Args:
            data_folder: Path to folder where JSON files should be stored
        """
        # Use the provided folder or default to project data folder
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        self.data_folder = data_folder or os.path.join(self.base_dir, 'data')

        # Ensure the data folder exists
        os.makedirs(self.data_folder, exist_ok=True)

        # Define file paths
        self.word_freq_file = os.path.join(self.data_folder, 'word_frequencies.json')
        self.hashtag_freq_file = os.path.join(self.data_folder, 'hashtag_frequencies.json')
        self.word_trends_file = os.path.join(self.data_folder, 'word_trends.json')
        self.engagement_file = os.path.join(self.data_folder, 'tweets_engagement.json')

        logger.info(f"JSON exporter initialized with data folder: {self.data_folder}")

    def export_word_frequencies(self, word_freq_data: Dict[str, Any]) -> bool:
        """
        Export word frequency data to JSON for dashboard visualization.

        Args:
            word_freq_data: Processed word frequency data from WordFrequencyProcessor

        Returns:
            Boolean indicating success/failure
        """
        try:
            # Format data specifically for visualization
            dashboard_data = {
                'words': word_freq_data.get('words', []),
                'total_words': word_freq_data.get('total_words', 0),
                'unique_words': word_freq_data.get('unique_words', 0),
                'period': word_freq_data.get('period', {}),
                'updated_at': datetime.now().isoformat()
            }

            # Save to file
            with open(self.word_freq_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=4)

            # If trending data is available, save it separately
            if 'trending' in word_freq_data and word_freq_data['trending']:
                trending_data = {
                    'trending_words': word_freq_data['trending'],
                    'period': word_freq_data.get('period', {}),
                    'updated_at': datetime.now().isoformat()
                }

                with open(self.word_trends_file, 'w', encoding='utf-8') as f:
                    json.dump(trending_data, f, ensure_ascii=False, indent=4)

            logger.info(f"Word frequency data exported to {self.word_freq_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting word frequencies to JSON: {str(e)}", exc_info=True)
            return False
    
    def export_hashtag_frequencies(self, hashtag_freq_data: Dict[str, Any]) -> bool:
        """
        Export hashtag frequency data to JSON for dashboard visualization.
        
        Args:
            word_freq_data: Processed word frequency data from HashFrequencyProcessor
            
        Returns:
            Boolean indicating success/failure
        """
        try:
            # Format data specifically for visualization
            dashboard_data = {
                'hashtags': hashtag_freq_data.get('hashtags', []), 
                'total_hashtags': hashtag_freq_data.get('total_hashtags', 0), 
                'unique_hashtags': hashtag_freq_data.get('unique_hashtags', 0),  
                'total_processed': hashtag_freq_data.get('total_processed', 0), 
                'period': hashtag_freq_data.get('period', {}),  
                'updated_at': datetime.now().isoformat()
            }

            
            # Save to file
            with open(self.hashtag_freq_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=4)
                
            logger.info(f"hashtag frequency data exported to {self.word_freq_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting word frequencies to JSON: {str(e)}", exc_info=True)
            return False
    
    def export_engagement_data(self, engagement_data: Dict[str, Any]) -> bool:
        """
        Export engagement data to JSON for dashboard visualization.

        Args:
            engagement_data: Processed engagement data from EngagementProcessor

        Returns:
            Boolean indicating success/failure
        """
        try:
            # Format data specifically for visualization
            dashboard_data = {
                'top_posts': engagement_data.get('top_posts', []),
                'engagement_metrics': engagement_data.get('engagement_metrics', {}),
                'daily_trends': engagement_data.get('daily_trends', []),
                'period': {
                    'start': engagement_data.get('start_date'),
                    'end': engagement_data.get('end_date')
                },
                'analysis_type': engagement_data.get('analysis_type'),
                'platform': engagement_data.get('platform'),
                'updated_at': datetime.now().isoformat()
            }

            # Save to file
            with open(self.engagement_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=4)

            logger.info(f"Engagement data exported to {self.engagement_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting engagement data to JSON: {str(e)}", exc_info=True)
            return False

    def export_analysis_results(self, analysis_type: str, data: Dict[str, Any]) -> bool:
        """
        General method to export any type of analysis results.

        Args:
            analysis_type: Type of analysis ('word_frequency', 'engagement', 'hashtag_frequency' etc.)
            data: Processed analysis data

        Returns:
            Boolean indicating success/failure
        """
        # Map of analysis types to their handler methods
        handlers = {
            'word_frequency': self.export_word_frequencies,
            'engagement': self.export_engagement_data,
            'hashtag_frequency': self.export_word_frequencies,
            # Add more handlers as needed
        }

        if analysis_type in handlers:
            return handlers[analysis_type](data)
        else:
            logger.error(f"Unknown analysis type: {analysis_type}")
            return False
