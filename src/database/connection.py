"""
Creates a connection to the SQLite database specified by db_path.

Parameters:
db_path (str): The file path to the SQLite database.

Returns:
Connection: SQLite3 Connection object.

Raises:
sqlite3.Error: If an error occurs while connecting to the database.
"""

import sqlite3
from sqlite3 import Connection


def get_connection(db_path: str) -> Connection:
    """
    Creates a connection to the SQLite database specified by db_path.

    Parameters:
    db_path (str): The file path to the SQLite database.

    Returns:
    Connection: SQLite3 Connection object.

    Raises:
    sqlite3.Error: If an error occurs while connecting to the database.
    """
    try:
        conn = sqlite3.connect(db_path)
        print(f"Connection to SQLite DB successful: {db_path}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite DB: {e}")
        raise
