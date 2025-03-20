import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

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
            self.logger.info(f"Processing engagement metrics from {start_date} to {end_date}")
            
            # Fetch posts for analysis
            posts = self.tweet_model.fetch_posts(
                platform=platform,
                start_date=start_date,
                end_date=end_date
            )
            
            if not posts:
                self.logger.warning("No posts found for the specified criteria")
                return {"status": "no_data", "message": "No posts found for analysis"}
            
            # Initialize result structure
            results = {
                "analysis_type": "engagement",
                "platform": platform if platform else "all",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "total_posts": len(posts),
                "engagement_metrics": {
                    "total_likes": 0,
                    "total_retweets": 0,
                    "total_comments": 0,
                    "avg_likes_per_post": 0,
                    "avg_retweets_per_post": 0,
                    "avg_comments_per_post": 0
                },
                "daily_trends": [],
                "top_posts": [],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Calculate total metrics
            for post in posts:
                results["engagement_metrics"]["total_likes"] += post["likes"] or 0
                results["engagement_metrics"]["total_retweets"] += post["retweets"] or 0
                results["engagement_metrics"]["total_comments"] += post["comments"] or 0
            
            # Calculate averages
            post_count = len(posts)
            if post_count > 0:
                results["engagement_metrics"]["avg_likes_per_post"] = round(
                    results["engagement_metrics"]["total_likes"] / post_count, 2
                )
                results["engagement_metrics"]["avg_retweets_per_post"] = round(
                    results["engagement_metrics"]["total_retweets"] / post_count, 2
                )
                results["engagement_metrics"]["avg_comments_per_post"] = round(
                    results["engagement_metrics"]["total_comments"] / post_count, 2
                )
            
            # Calculate daily trends
            daily_metrics = defaultdict(lambda: {"posts": 0, "likes": 0, "retweets": 0, "comments": 0})
            for post in posts:
                date_str = post["post_date"].strftime("%Y-%m-%d")
                daily_metrics[date_str]["posts"] += 1
                daily_metrics[date_str]["likes"] += post["likes"] or 0
                daily_metrics[date_str]["retweets"] += post["retweets"] or 0
                daily_metrics[date_str]["comments"] += post["comments"] or 0
            
            # Format daily trends for output
            for date_str, metrics in sorted(daily_metrics.items()):
                results["daily_trends"].append({
                    "date": date_str,
                    "posts": metrics["posts"],
                    "likes": metrics["likes"],
                    "retweets": metrics["retweets"],
                    "comments": metrics["comments"],
                    "avg_likes": round(metrics["likes"] / metrics["posts"], 2) if metrics["posts"] > 0 else 0,
                    "avg_retweets": round(metrics["retweets"] / metrics["posts"], 2) if metrics["posts"] > 0 else 0,
                    "avg_comments": round(metrics["comments"] / metrics["posts"], 2) if metrics["posts"] > 0 else 0
                })
            
            # Find top posts by engagement (likes + retweets + comments)
            sorted_posts = sorted(
                posts, 
                key=lambda x: (x["likes"] or 0) + (x["retweets"] or 0) + (x["comments"] or 0),
                reverse=True
            )
            
            # Include top 10 posts by engagement
            for post in sorted_posts[:10]:
                results["top_posts"].append({
                    "id": post["id"],
                    "platform": post["platform"],
                    "post_date": post["post_date"].strftime("%Y-%m-%d"),
                    "post_time": post["post_time"].strftime("%H:%M:%S") if post["post_time"] else None,
                    "content": post["content"][:100] + "..." if len(post["content"]) > 100 else post["content"],
                    "likes": post["likes"] or 0,
                    "retweets": post["retweets"] or 0,
                    "comments": post["comments"] or 0,
                    "total_engagement": (post["likes"] or 0) + (post["retweets"] or 0) + (post["comments"] or 0)
                })
            
            self.logger.info(f"Engagement analysis complete. Processed {len(posts)} posts.")
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing engagement metrics: {str(e)}")
            raise
