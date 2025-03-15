import mysql.connector
from mysql.connector import Error
import logging


class DatabaseConnection:
    """
    A class to manage database connections to MySQL/MariaDB.
    Provides connection pooling and error handling functionality.
    """

    def __init__(self, host='localhost', user='root', password='', database='social_media_pipeline', pool_size=5):
        """
        Initialize the database connection with configurable parameters.

        Args:
            host (str): Database host
            user (str): Database username
            password (str): Database password
            database (str): Database name
            pool_size (int): Size of the connection pool
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.pool_size = pool_size
        self.pool = None
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

    def get_connection_pool(self):
        """
        Create and return a connection pool.

        Returns:
            mysql.connector.pooling.MySQLConnectionPool: A connection pool
        """
        if self.pool is None:
            try:
                self.pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="social_media_pool",
                    pool_size=self.pool_size,
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=False,  # We'll manage transactions explicitly
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci'
                )
                self.logger.info(f"Connection pool created with size {self.pool_size}")
            except Error as e:
                self.logger.error(f"Error creating connection pool: {e}")
                raise
        return self.pool

    def get_connection(self):
        """
        Get a connection from the pool or create a new one if pool is not available.

        Returns:
            mysql.connector.connection.MySQLConnection: A database connection
        """
        try:
            # Try to get from pool first
            if self.pool:
                return self.pool.get_connection()

            # Fall back to direct connection
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            if connection.is_connected():
                self.logger.debug("Connected to database")
            return connection
        except Error as e:
            self.logger.error(f"Error connecting to database: {e}")
            raise

    def close_all_connections(self):
        """Close all connections in the pool"""
        if self.pool:
            try:
                # In some mysql.connector versions, this method exists
                if hasattr(self.pool, 'close'):
                    self.pool.close()
                self.pool = None
                self.logger.info("All connections closed")
            except Exception as e:
                self.logger.error(f"Error closing connections: {e}")
