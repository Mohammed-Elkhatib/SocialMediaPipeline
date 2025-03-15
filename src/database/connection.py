import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    def __init__(self, host='localhost', user='root', password='', database='social_media_pipeline'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def get_db_connection(self):
        """Return the database connection."""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if connection.is_connected():
                print("Connected to database")
            return connection
        except Error as e:
            print(f"Error: {e}")
            return None
