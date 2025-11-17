import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from backend.config import Config

class Database:
    @staticmethod
    def get_connection():
        """Create and return a database connection"""
        try:
            connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=False
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    @staticmethod
    @contextmanager
    def get_cursor(dictionary=True):
        """Context manager for database cursor"""
        connection = Database.get_connection()
        cursor = connection.cursor(dictionary=dictionary)
        try:
            yield cursor, connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def execute_query(query, params=None, fetch=False, fetch_one=False):
        """Execute a query and optionally fetch results"""
        with Database.get_cursor() as (cursor, connection):
            cursor.execute(query, params or ())

            if fetch_one:
                return cursor.fetchone()
            elif fetch:
                return cursor.fetchall()
            else:
                connection.commit()
                return cursor.lastrowid
