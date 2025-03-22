import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class EngagementProcessor:
    """Processor for analyzing engagement metrics like likes, retweets, and comments"""

    def __init__(self, tweet_model):
        self.tweet_model = tweet_model
        self.logger = logging.getLogger(__name__)

    def process(self, start_date: datetime, end_date: datetime, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Process engagement metrics for posts within the given date range.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            platform: Platform to analyze ('x', 'facebook', or None for all)

        Returns:
            Dictionary containing engagement analysis results
        """
        try:
            date_range = f"from {start_date} to {end_date}" if start_date and end_date else "all time"
            self.logger.info(f"Processing engagement metrics for {platform} {date_range}")

            # Get aggregate metrics directly from SQL
            metrics = self.tweet_model.fetch_engagement_metrics(platform, start_date, end_date)

            if not metrics or metrics.get('total_posts', 0) == 0:
                self.logger.warning("No posts found for the specified criteria")
                return {"status": "no_data", "message": "No posts found for analysis"}

            # Get daily trends from SQL
            daily_trends = self.tweet_model.fetch_daily_engagement_trends(platform, start_date, end_date)

            # Format date strings in daily trends
            for trend in daily_trends:
                if isinstance(trend.get('date'), datetime):
                    trend['date'] = trend['date'].strftime("%Y-%m-%d")

                # Round average values
                for key in ['avg_likes', 'avg_retweets', 'avg_comments']:
                    if key in trend and trend[key] is not None:
                        trend[key] = round(trend[key], 2)

            # Get top posts sorted by engagement
            top_posts = self.tweet_model.fetch_posts(
                platform=platform,
                start_date=start_date,
                end_date=end_date,
                sort_by="engagement",
                limit=10
            )

            # Format top posts for output
            formatted_top_posts = []
            for post in top_posts:
                formatted_post = {
                    "id": post["id"],
                    "platform": post["platform"],
                    "post_date": post["post_date"].strftime("%Y-%m-%d") if isinstance(post["post_date"], datetime) else
                    post["post_date"],
                    "post_time": post["post_time"].strftime("%H:%M:%S") if post["post_time"] and isinstance(
                        post["post_time"], datetime) else post["post_time"],
                    "content": post["content"][:100] + "..." if len(post["content"]) > 100 else post["content"],
                    "likes": post["likes"] or 0,
                    "retweets": post["retweets"] or 0,
                    "comments": post["comments"] or 0,
                    "total_engagement": (post["likes"] or 0) + (post["retweets"] or 0) + (post["comments"] or 0)
                }
                formatted_top_posts.append(formatted_post)

            # Build results structure
            results = {
                "analysis_type": "engagement",
                "platform": platform if platform else "all",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "total_posts": metrics['total_posts'],
                "engagement_metrics": {
                    "total_likes": metrics['total_likes'] or 0,
                    "total_retweets": metrics['total_retweets'] or 0,
                    "total_comments": metrics['total_comments'] or 0,
                    "avg_likes_per_post": round(metrics['avg_likes_per_post'] or 0, 2),
                    "avg_retweets_per_post": round(metrics['avg_retweets_per_post'] or 0, 2),
                    "avg_comments_per_post": round(metrics['avg_comments_per_post'] or 0, 2)
                },
                "daily_trends": daily_trends,
                "top_posts": formatted_top_posts,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            self.logger.info(f"Engagement analysis complete. Processed {metrics['total_posts']} posts.")
            return results

        except Exception as e:
            self.logger.error(f"Error processing engagement metrics: {str(e)}")
            raise
