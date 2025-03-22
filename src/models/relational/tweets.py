from datetime import datetime, timedelta
from src.models.relational.connection import DatabaseConnection
import mysql.connector
import logging
from decimal import Decimal


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

    def execute_many(self, query, params):
        """Execute a batch query with many parameters."""
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params)
            conn.commit()
            cursor.close()
        except Exception as e:
            self.db_connection.get_connection().rollback()
            self.logger.error(f"Database error: {e}")
            raise

    def insert_post(self, post_id, post_date, post_time, content, likes, retweets, comments):
        """Insert post data for a specific platform or update if it already exists."""

        insert_post_query = """
            INSERT INTO posts (id, platform, post_date, post_time, content, likes, retweets, comments, scraped_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                likes = VALUES(likes),
                retweets = VALUES(retweets),
                comments = VALUES(comments),
                scraped_at = NOW();
        """

        params = (post_id, 'x', post_date, post_time, content, likes, retweets, comments)
        self.logger.debug(f"Executing insert_post_query with params: {params}")
        self.execute_query(insert_post_query, params)
        self.logger.info("Post inserted or updated successfully.")

    def insert_word_frequencies(self, word_frequencies):
        """Insert word frequency data into the database using batch processing."""

        if not word_frequencies:
            self.logger.info("No word frequencies to insert.")
            return

        # Prepare batch parameters for efficient insertion
        params = []
        for word, frequency in word_frequencies.items():
            params.append(('x', word, frequency))

        # Use executemany for batch processing
        insert_word_frequencies_query = """
            INSERT INTO word_frequency (id, word, count)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE count = count + VALUES(count)
        """

        self.execute_many(insert_word_frequencies_query, params)
        self.logger.info(f"Word frequencies batch inserted successfully: {len(params)} words processed.")

    def insert_hashtag_frequencies(self, word_frequencies):
        """Insert hashtag frequency data into the database using batch processing."""

        if not word_frequencies:
            self.logger.info("No hashtag frequencies to insert.")
            return

        # Prepare batch parameters for efficient insertion
        params = []
        for word, frequency in word_frequencies.items():
            params.append(('x', word, frequency))

        # Use executemany for batch processing
        insert_word_frequencies_query = """
            INSERT INTO hashtag_frequency (id, word, count)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE count = count + VALUES(count)
        """

        self.execute_many(insert_word_frequencies_query, params)
        self.logger.info(f"Word frequencies batch inserted successfully: {len(params)} words processed.")

    def update_top_comments(self, comments_data):
        """Update top comments using REPLACE INTO to handle both inserts and updates."""

        if not comments_data:
            self.logger.info("No comment data to update.")
            return

        # First, verify all posts exist to avoid foreign key constraint violations
        post_ids = [comment['id'] for comment in comments_data if 'id' in comment]
        if not post_ids:
            self.logger.warning("No valid post IDs found in comments data.")
            return

        # Use REPLACE INTO instead of deleting everything first
        replace_query = """
            REPLACE INTO top_comments (post_id, comments_count, created_at)
            VALUES (%s, %s, NOW());
        """

        for comment in comments_data:
            post_id = comment.get('id')
            comments_count = comment.get('comments')

            if post_id and comments_count is not None:
                params = (post_id, comments_count)
                self.execute_query(replace_query, params)
                self.logger.info(f"Updated comments for post {post_id}: {comments_count}")
            else:
                self.logger.warning(f"Skipping invalid comment data: {comment}")

    def update_top_likes(self, likes_data):
        """Update top likes using REPLACE INTO to handle both inserts and updates."""

        if not likes_data:
            self.logger.info("No likes data to update.")
            return

        # Use REPLACE INTO instead of deleting everything first
        replace_query = """
            REPLACE INTO top_likes (post_id, likes_count, created_at)
            VALUES (%s, %s, NOW());
        """

        for like in likes_data:
            post_id = like.get('id')
            likes_count = like.get('likes')

            if post_id and likes_count is not None:
                params = (post_id, likes_count)
                self.execute_query(replace_query, params)
                self.logger.info(f"Updated likes for post {post_id}: {likes_count}")
            else:
                self.logger.warning(f"Skipping invalid likes data: {like}")

    def update_top_retweets(self, retweets_data):
        """Update top retweets using REPLACE INTO to handle both inserts and updates."""

        if not retweets_data:
            self.logger.info("No retweets data to update.")
            return

        # Use REPLACE INTO instead of deleting everything first
        replace_query = """
            REPLACE INTO top_retweets (post_id, retweets_count, created_at)
            VALUES (%s, %s, NOW());
        """

        for retweet in retweets_data:
            post_id = retweet.get('id')
            retweets_count = retweet.get('retweets')

            if post_id and retweets_count is not None:
                params = (post_id, retweets_count)
                self.execute_query(replace_query, params)
                self.logger.info(f"Updated retweets for post {post_id}: {retweets_count}")
            else:
                self.logger.warning(f"Skipping invalid retweets data: {retweet}")

    def fetch_posts(self, platform='x', start_date=None, end_date=None, sort_by="post_date", limit=None):
        """Fetch posts with flexible sorting options.

        Args:
            platform (str): Filter by platform name ('x' or 'facebook')
            start_date (date): Filter posts on or after this date
            end_date (date): Filter posts on or before this date
            sort_by (str): Field to sort by ('post_date', 'scraped_at', or 'engagement')
            limit (int): Maximum number of records to return

        Returns:
            list: List of posts matching the criteria
        """
        # Determine if we need to calculate engagement
        calculate_engagement = (sort_by == "engagement")

        # Build the base query with conditional total_engagement field
        query = """
            SELECT 
                id, 
                platform, 
                post_date, 
                post_time, 
                content, 
                likes,
                retweets,
                comments,
                scraped_at
        """

        # Only add total_engagement to the SELECT if we're sorting by it
        if calculate_engagement:
            query += ", (likes + retweets + comments) as total_engagement"

        query += """
            FROM posts
            WHERE 1=1
        """
        params = []

        # Add filters if provided
        if platform:
            query += " AND platform = %s"
            params.append(platform)

        if start_date:
            query += " AND post_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND post_date <= %s"
            params.append(end_date)

        # Apply sorting based on user preference
        if sort_by == "engagement":
            query += " ORDER BY total_engagement DESC"
        elif sort_by == "scraped_at":
            query += " ORDER BY scraped_at DESC"
        else:  # Default to post_date, post_time
            query += " ORDER BY post_date DESC, post_time DESC"

        # Add limit if provided
        if limit:
            query += " LIMIT %s"
            params.append(limit)

        return self.execute_query(query, tuple(params))

    def fetch_top_comments(self, limit=10):
        """Fetch the top commented posts."""
        fetch_top_comments_query = """
            SELECT 
                t.post_id, 
                p.content, 
                p.post_date, 
                p.post_time,
                p.likes, 
                p.retweets, 
                p.comments, 
                t.created_at
            FROM top_comments t
            JOIN posts p ON t.post_id = p.id
            ORDER BY p.comments DESC
            LIMIT %s;
        """
        return self.execute_query(fetch_top_comments_query, (limit,))

    def fetch_top_likes(self, limit=10):
        """Fetch the top liked posts."""
        fetch_top_likes_query = """
            SELECT 
                t.post_id, 
                p.content, 
                p.post_date, 
                p.post_time,
                p.likes, 
                p.retweets, 
                p.comments, 
                t.created_at
            FROM top_likes t
            JOIN posts p ON t.post_id = p.id
            ORDER BY p.likes DESC
            LIMIT %s;
        """
        return self.execute_query(fetch_top_likes_query, (limit,))

    def fetch_top_retweets(self, limit=10):
        """Fetch the top retweeted posts."""
        fetch_top_retweets_query = """
            SELECT 
                t.post_id, 
                p.content, 
                p.post_date, 
                p.post_time,
                p.likes, 
                p.retweets, 
                p.comments, 
                t.created_at
            FROM top_retweets t
            JOIN posts p ON t.post_id = p.id
            ORDER BY p.retweets DESC
            LIMIT %s;
        """
        return self.execute_query(fetch_top_retweets_query, (limit,))
    def fetch_total_retweets(self):
        """Fetch total count of retweets from posts."""
        fetch_total_retweets_query = """
            SELECT sum(p.retweets) 
            FROM posts p;
        """
        result = self.execute_query(fetch_total_retweets_query)
        # Ensure you handle the case where the result might be empty or None
        return result[0]['sum(p.retweets)'] if result and result[0]['sum(p.retweets)'] is not None else 0

    def fetch_total_comments(self):
        """Fetch total count of comments from posts."""
        fetch_total_comments_query = """
            SELECT sum(p.comments) 
            FROM posts p;
        """
        result = self.execute_query(fetch_total_comments_query)
        # Ensure it returns an integer value
        return int(result[0]['sum(p.comments)']) if result and result[0]['sum(p.comments)'] is not None else 0

    def fetch_total_posts(self):
        """Fetch total count of posts."""
        fetch_total_posts_query = """
            SELECT count(p.id) 
            FROM posts p;
        """
        result = self.execute_query(fetch_total_posts_query)
        return result[0]['count(p.id)'] if result and result[0]['count(p.id)'] is not None else 0

    def fetch_total_likes(self):
        """Fetch total count of likes from posts."""
        fetch_total_likes_query = """
            SELECT sum(p.likes) 
            FROM posts p;
        """
        result = self.execute_query(fetch_total_likes_query)
        # Ensure it returns an integer value, not a dict or list
        return int(result[0]['sum(p.likes)']) if result and result[0]['sum(p.likes)'] is not None else 0

    def fetch_word_frequencies(self, platform=None, limit=100):
        """Fetch the word frequencies, optionally filtered by platform."""
        query = """
            SELECT word, count
            FROM word_frequency
            WHERE 1=1
        """
        params = []

        if platform:
            query += " AND id = %s"
            params.append(platform)

        query += " ORDER BY count DESC LIMIT %s"
        params.append(limit)

        return self.execute_query(query, tuple(params))
    
    def fetch_hashtag_frequencies(self, platform=None, limit=100):
        """Fetch the hashtag frequencies, optionally filtered by platform."""
        query = """
            SELECT word, count
            FROM hashtag_frequency
            WHERE 1=1
        """
        params = []

        if platform:
            query += " AND id = %s"
            params.append(platform)

        query += " ORDER BY count DESC LIMIT %s"
        params.append(limit)

        return self.execute_query(query, tuple(params))

    def fetch_post_by_id(self, post_id):
        """Fetch a specific post by its ID."""
        fetch_post_query = """
            SELECT 
                id, 
                platform, 
                post_date, 
                post_time, 
                content, 
                likes,
                retweets,
                comments,
                scraped_at
            FROM posts
            WHERE id = %s
        """
        results = self.execute_query(fetch_post_query, (post_id,))
        return results[0] if results else None

    def _build_base_posts_query(self, platform=None, start_date=None, end_date=None):
        """Helper to build the common WHERE clause for posts queries."""
        query_fragment = "WHERE 1=1"
        params = []

        if platform:
            query_fragment += " AND platform = %s"
            params.append(platform)

        if start_date:
            query_fragment += " AND post_date >= %s"
            params.append(start_date)

        if end_date:
            query_fragment += " AND post_date <= %s"
            params.append(end_date)

        return query_fragment, params

    def fetch_engagement_metrics(self, platform=None, start_date=None, end_date=None):
        """Fetch aggregated engagement metrics for the given criteria."""
        where_clause, params = self._build_base_posts_query(platform, start_date, end_date)

        query = f"""
            SELECT 
                COUNT(*) as total_posts,
                SUM(likes) as total_likes,
                SUM(retweets) as total_retweets,
                SUM(comments) as total_comments,
                AVG(likes) as avg_likes_per_post,
                AVG(retweets) as avg_retweets_per_post,
                AVG(comments) as avg_comments_per_post
            FROM posts
            {where_clause}
        """

        results = self.execute_query(query, tuple(params))
        return results[0] if results else None

    def fetch_daily_engagement_trends(self, platform=None, start_date=None, end_date=None):
        """Fetch daily engagement trends grouped by post date."""
        where_clause, params = self._build_base_posts_query(platform, start_date, end_date)

        query = f"""
            SELECT 
                post_date as date,
                COUNT(*) as posts,
                SUM(likes) as likes,
                SUM(retweets) as retweets,
                SUM(comments) as comments,
                AVG(likes) as avg_likes,
                AVG(retweets) as avg_retweets,
                AVG(comments) as avg_comments
            FROM posts
            {where_clause}
            GROUP BY post_date 
            ORDER BY post_date
        """

        return self.execute_query(query, tuple(params))

    def fetch_top_posts_by_engagement(self, platform=None, start_date=None, end_date=None, limit=10):
        """Fetch top posts by total engagement (likes + retweets + comments)."""
        where_clause, params = self._build_base_posts_query(platform, start_date, end_date)

        query = f"""
            SELECT 
                id,
                platform,
                post_date,
                post_time,
                content,
                likes,
                retweets,
                comments,
                (likes + retweets + comments) as total_engagement
            FROM posts
            {where_clause}
            ORDER BY total_engagement DESC 
            LIMIT %s
        """
        params.append(limit)

        return self.execute_query(query, tuple(params))
    
    def fetch_engagement_data(self):
        # Query to fetch data for the past 5 days
        query = """
        SELECT 
            DATE(p.post_date) AS day,
            COUNT(p.id) AS post_count,
            SUM(p.likes) AS total_likes,
            SUM(p.retweets) AS total_retweets,
            SUM(p.comments) AS total_comments
        FROM posts p
        WHERE p.post_date >= CURRENT_DATE - INTERVAL 5 DAY
        GROUP BY day
        ORDER BY day DESC;
        """

        results = self.execute_query(query)

        engagement_data = []
        for row in results:
            # Now use dictionary keys instead of tuple indices
            total_engagement = row["total_likes"] + row["total_retweets"] + row["total_comments"]
            engagement_per_post = total_engagement / row["post_count"] if row["post_count"] > 0 else 0
            engagement_data.append({
                "day": row["day"],
                "post_count": row["post_count"],
                "total_likes": row["total_likes"],
                "total_retweets": row["total_retweets"],
                "total_comments": row["total_comments"],
                "total_engagement": total_engagement,
                "engagement_per_post": engagement_per_post
            })
            
        return engagement_data
    
    def fetch_heatmap_raw_data(self):
        query = """
        SELECT
            DATE(p.post_date) AS day,
            CASE 
                WHEN HOUR(p.post_time) >= 6 AND HOUR(p.post_time) < 12 THEN 'Morning'
                WHEN HOUR(p.post_time) >= 12 AND HOUR(p.post_time) < 18 THEN 'Afternoon'
                ELSE 'Evening'
            END AS time_of_day,
            COUNT(p.id) AS count
        FROM posts p
        GROUP BY day, time_of_day
        ORDER BY day ASC;
        """
        # Execute the query – assumes your execute_query returns a list of dictionaries
        raw_data = self.execute_query(query)
        return raw_data
    
    def fetch_virality_data(self):
        query = """
        SELECT 
            p.id,
            p.post_date,
            p.post_time,
            p.likes,
            p.retweets,
            p.comments
        FROM posts p
        """
        results = self.execute_query(query)
        
        virality_data = []
        current_time = datetime.now()  # Get the current date and time
        
        for row in results:
            # Get engagement metrics
            total_engagement = row["likes"] + row["retweets"] + row["comments"]
            # Check if post_time is a timedelta, and convert it into time format
            if isinstance(row["post_time"], timedelta):
                total_seconds = row["post_time"].total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                post_time = datetime.min.replace(hour=hours, minute=minutes, second=seconds).time()
            else:
                post_time = row["post_time"]  # In case it's already a time object

            # Combine 'post_date' and 'post_time' into a single datetime object
            post_datetime = datetime.combine(row["post_date"], post_time)

            # Get time difference in seconds
            time_diff = (current_time - post_datetime).total_seconds()/3600

            # Prevent division by zero (if time_diff is 0)
            if time_diff == 0:
                time_diff = 1  # To avoid dividing by zero

            # Calculate virality score, convert avg_engagement_per_post to float
            virality_score = float(total_engagement) / time_diff

            # Store the results
            virality_data.append({
                "post_id": row["id"],
                "post_date": row["post_date"],
                "virality_score": virality_score,
            })
        
        return virality_data