from connection import DatabaseConnection
import mysql.connector
import logging


class TweetModel:
    """
    Handles database operations related to tweets and their engagement metrics.
    """

    def __init__(self):
        self.db_connection = DatabaseConnection()
        self._setup_logger()

    def _setup_logger(self):
        """Configure logger for database operations"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def seed_platforms(self):
        """Seed the platforms table with Facebook and X if they do not already exist."""

        # Query to check if platforms 'facebook' and 'x' already exist
        check_platforms_query = "SELECT name FROM platforms WHERE name IN (%s, %s)"
        params = ('facebook', 'x')
        existing_platforms = self.execute_query(check_platforms_query, params)

        # If platforms are not found, insert them
        if not existing_platforms:
            insert_query = """
                INSERT INTO platforms (name) 
                VALUES (%s), (%s)
            """
            self.execute_query(insert_query, params)
            self.logger.info("Platforms seeded successfully.")
        else:
            self.logger.info("Platforms already exist.")

    def execute_query(self, query, params=None):
        """Generic method to execute a query."""
        try:
            connection = self.db_connection.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            connection.commit()
            connection.close()
            return result
        except mysql.connector.Error as err:
            self.logger.error(f"Error: {err}")
            return None

    def fetch_posts(self, platform=None, start_date=None, end_date=None):
        """Fetch posts for a specific platform or all platforms."""
        query = "SELECT p.id, p.platform_id, p.post_date, p.post_time, p.content, p.scraped_at, pf.name AS platform_name " \
                "FROM posts p JOIN platforms pf ON p.platform_id = pf.id WHERE 1=1"
        params = []

        if platform:
            query += " AND pf.name = %s"
            params.append(platform)

        if start_date:
            query += " AND p.post_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND p.post_date <= %s"
            params.append(end_date)

        return self.execute_query(query, tuple(params))

    def fetch_engagement_metrics(self, platform=None, start_date=None, end_date=None):
        """Fetch engagement metrics for a specific platform or all platforms."""
        query = "SELECT e.likes, e.retweets, e.comments, p.post_date, p.post_time, pf.name AS platform_name " \
                "FROM engagement_metrics e " \
                "JOIN posts p ON e.post_id = p.id " \
                "JOIN platforms pf ON e.platform_id = pf.id WHERE 1=1"
        params = []

        if platform:
            query += " AND pf.name = %s"
            params.append(platform)

        if start_date:
            query += " AND p.post_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND p.post_date <= %s"
            params.append(end_date)

        return self.execute_query(query, tuple(params))

    def insert_post_and_engagement_metrics(self, platform, post_date, post_time, content, likes, retweets, comments):
        self.seed_platforms()

        """Insert post data and engagement metrics for a specific platform."""

        # Step 1: Insert the Post into the 'posts' table
        insert_post_query = """
            INSERT INTO posts (platform_id, post_date, post_time, content)
            SELECT id, %s, %s, %s
            FROM platforms
            WHERE name = %s
            ON DUPLICATE KEY UPDATE post_date = post_date;  -- Avoid duplicate entries
        """
        params = (post_date, post_time, content, platform)
        self.logger.debug(f"Executing insert_post_query with params: {params}")
        self.execute_query(insert_post_query, params)

        # Step 2: Retrieve the post ID of the recently inserted post
        select_post_id_query = """
            SELECT p.id 
            FROM posts p
            JOIN platforms pf ON p.platform_id = pf.id
            WHERE pf.name = %s AND p.post_date = %s AND p.post_time = %s
            ORDER BY p.id DESC LIMIT 1
        """
        params = (platform, post_date, post_time)
        self.logger.debug(f"Executing select_post_id_query with params: {params}")
        post = self.execute_query(select_post_id_query, params)

        if post:
            post_id = post[0]['id']
            self.logger.debug(f"Retrieved post ID: {post_id}")
        else:
            self.logger.error("Error: Post ID retrieval failed.")
            return

        # Step 3: Insert the Engagement Metrics into the 'engagement_metrics' table
        insert_engagement_query = """
            INSERT INTO engagement_metrics (likes, retweets, comments, platform_id, post_id)
            VALUES (%s, %s, %s, (SELECT id FROM platforms WHERE name = %s), %s)
        """
        params = (likes, retweets, comments, platform, post_id)
        self.execute_query(insert_engagement_query, params)

        self.logger.info("Post and engagement metrics inserted successfully.")

    def insert_word_frequencies(self, word_frequencies):
        """Insert word frequency data into the database."""
        insert_word_frequencies_query = """
            INSERT INTO word_frequency (word, count)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE count = count + VALUES(count)
        """
        for word, frequency in word_frequencies.items():
            params = (word, frequency)
            self.execute_query(insert_word_frequencies_query, params)

        self.logger.info(f"Word frequencies inserted successfully.")

    def insert_top_comments(self, comments_data, platform_name):
        """Clear all previous top comments and insert a new batch with post details."""

        # Step 1: Delete the previous records in top_comments table
        delete_top_comments_query = "DELETE FROM top_comments"
        self.execute_query(delete_top_comments_query)

        # Step 2: Insert top comments based on the incoming comments_data
        for comment in comments_data:
            post_date = comment.get('post_date') or comment.get('date')
            post_time = comment.get('post_time') or comment.get('time')
            content = comment.get('content', '')
            post_id = self.get_post_id(post_date, post_time, platform_name)

            if post_id:
                insert_top_comments_query = """
                    INSERT INTO top_comments (post_id, created_at)
                    VALUES (%s, NOW());
                """
                params = (post_id,)
                self.execute_query(insert_top_comments_query, params)
                self.logger.info(f"Inserted comment for post {post_id} at {post_date} {post_time}")
            else:
                self.logger.warning(
                    f"Error: Post not found for comment '{content[:30]}...' with post_date {post_date} and post_time {post_time}")

    def insert_top_likes(self, likes_data, platform_name):
        """Clear all previous top likes and insert a new batch with post details."""

        # Step 1: Delete the previous records in top_likes table
        delete_top_likes_query = "DELETE FROM top_likes"
        self.execute_query(delete_top_likes_query)

        # Step 2: Insert top comments based on the incoming comments_data
        for like in likes_data:
            post_date = like.get('post_date') or like.get('date')
            post_time = like.get('post_time') or like.get('time')
            content = like.get('content', '')
            post_id = self.get_post_id(post_date, post_time, platform_name)

            if post_id:
                insert_top_likes_query = """
                    INSERT INTO top_likes (post_id, created_at)
                    VALUES (%s, NOW());
                """
                params = (post_id,)
                self.execute_query(insert_top_likes_query, params)
                self.logger.info(f"Inserted likes for post {post_id} at {post_date} {post_time}")
            else:
                self.logger.warning(
                    f"Error: Post not found for like '{content[:30]}...' with post_date {post_date} and post_time {post_time}")

    def get_post_id(self, post_date, post_time, platform_name):
        """Fetch the post_id based on date, time, and platform name."""
        query = """
            SELECT p.id 
            FROM posts p
            JOIN platforms pf ON p.platform_id = pf.id
            WHERE p.post_date = %s
              AND p.post_time = %s
              AND pf.name = %s
        """
        params = (post_date, post_time, platform_name)
        result = self.execute_query(query, params)

        if result:
            return result[0]['id']
        return None

    def fetch_top_comments(self):
        """Fetch the top comments."""
        fetch_top_comments_query = """
            SELECT t.post_id, p.content, p.post_date as date, p.post_time as time, e.likes, e.retweets, e.comments, t.created_at
            FROM top_comments t
            JOIN posts p ON t.post_id = p.id
            JOIN engagement_metrics e ON e.post_id = p.id 
            ORDER BY t.created_at DESC;
        """
        return self.execute_query(fetch_top_comments_query)

    def fetch_top_likes(self):
        """Fetch the top liked posts."""
        fetch_top_likes_query = """
            SELECT t.post_id, p.content, p.post_date as date, p.post_time as time, e.likes, e.retweets, e.comments, t.created_at
            FROM top_likes t
            JOIN posts p ON t.post_id = p.id
            JOIN engagement_metrics e ON e.post_id = p.id 
            ORDER BY t.created_at DESC;
        """
        return self.execute_query(fetch_top_likes_query)

    def fetch_word_frequencies(self):
        """Fetch the word frequencies for a specific post."""
        fetch_word_frequencies_query = """
            SELECT word, count
            FROM word_frequency
            ORDER BY count DESC;
        """
        return self.execute_query(fetch_word_frequencies_query)
