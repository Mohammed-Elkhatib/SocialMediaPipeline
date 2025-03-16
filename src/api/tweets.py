from src.models.relational.tweets import TweetModel


class TweetAPI:
    """
    API class to provide access to tweet data for the front-end or reporting.
    """

    def __init__(self):
        self.tweet_model = TweetModel()

    def get_recent_tweets(self, platform=None, limit=20):
        """
        Get the most recent tweets.

        Args:
            platform (str): Filter by platform name ('x', 'facebook')
            limit (int): Maximum number of tweets to return

        Returns:
            list: List of tweets with engagement metrics
        """
        tweets = self.tweet_model.fetch_posts(sort_by="scraped_at")

        # Limit the results
        if tweets and limit:
            tweets = tweets[:limit]

        return tweets

    def get_top_liked_tweets(self):
        """
        Get the tweets with the most likes.

        Returns:
            list: List of top liked tweets
        """
        return self.tweet_model.fetch_top_likes()

    def get_top_commented_tweets(self):
        """
        Get the tweets with the most comments.

        Returns:
            list: List of top commented tweets
        """
        return self.tweet_model.fetch_top_comments()

    def get_word_frequencies(self, limit=20):
        """
        Get the most frequent words from the tweets.

        Args:
            limit (int): Maximum number of words to return

        Returns:
            list: List of words and their frequencies
        """
        word_freqs = self.tweet_model.fetch_word_frequencies()

        # Limit the results
        if word_freqs and limit:
            word_freqs = word_freqs[:limit]

        return word_freqs
