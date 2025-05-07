"""
This module provides various database operations for managing and interacting with an SQLite
database. It includes functions to execute queries, save data, create tables, and retrieve data from
the database.
Functions:
    execute_query_with_management(
        db_path: str, query: str, params: tuple = (), fetch: bool = False
    ):
    save_to_sqlite(
        df: pd.DataFrame, db_path: str, table_name: str, if_exists: str = "append"
    ) -> None:
    save_topics_to_db(db_path: str, sentiment: str, topics: str):
    create_article_analysis_table(db_path: str):
    insert_article_analysis(db_path: str, results: list):
    get_article_analysis_topics_by_sentiment(db_path: str, sentiment):
    get_articles(db_path: str):
    get_subjectivity_distribution(db_path: str):
    get_objective_articles(db_path: str, threshold=0.5):
    get_subjective_articles(db_path: str, threshold=0.5):
    correlate_subjectivity_sentiment(db_path: str):
    get_articles_by_sentiment(db_path: str, sentiment):
    create_analysis_table(db_path):
    insert_analysis_data(db_path, title, article_text, topics, entities, coherence_score):
    drop_table(database_path, table_name):
    save_analysis_data(db_path, title, article_text, topics, entities, coherence_scores):
"""

import sqlite3

import pandas as pd

from .connection import get_connection


def execute_query_with_management(
    db_path: str,
    query: str,
    params: tuple = (),
    fetch: bool = False,
    many: bool = False,
):
    """
    Executes a query and manages the connection's activity including commit, close, and cursor
    execute. Can also execute many queries if specified.

    Parameters:
    db_path (str):
        The file path to the SQLite database.
    query (str):
        The SQL query to be executed.
    params (tuple or list of tuples):
        Parameters for the SQL query. If many is True, this should be a list of tuples.
    fetch (bool):
        Whether to fetch the results of the query.
    many (bool):
        Whether to execute many queries.

    Returns:
    list or None: The fetched results if fetch is True, otherwise None.
    """
    result = None

    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        if many:
            cursor.executemany(query, params)
        elif fetch:
            cursor.execute(query, params)
            result = cursor.fetchall()
        else:
            cursor.execute(query, params)
        conn.commit()
        print("Query executed successfully.")
    finally:
        conn.close()

    return result


def save_to_sqlite(
    df: pd.DataFrame, db_path: str, table_name: str, if_exists: str = "append"
) -> None:
    """
    Save a pandas DataFrame to an SQLite database.

    Parameters:
    df (pd.DataFrame): The DataFrame to be saved.
    db_path (str): The file path to the SQLite database.
    table_name (str): The name of the table to save the DataFrame to.
    if_exists (str): What to do if the table already exists.

    Returns:
    None
    """
    with get_connection(db_path) as conn:  # Use get_connection
        df.to_sql(
            table_name, con=conn, if_exists=if_exists, index=False, chunksize=1000
        )
    print("Data saved to SQLite successfully.")


def save_topics_to_db(db_path: str, sentiment: str, topics: str):
    """
    Saves topics to the database.

    Parameters:
    db_path (str): The file path to the SQLite database.
    sentiment (str): The sentiment of the topics.
    topics (str): The topics to be saved.

    Returns:
    None
    """
    execute_query_with_management(
        db_path, "CREATE TABLE IF NOT EXISTS topics (sentiment TEXT, topics TEXT)"
    )
    execute_query_with_management(
        db_path,
        "INSERT INTO topics (sentiment, topics) VALUES (?, ?)",
        (sentiment, str(topics)),
    )


def create_article_analysis_table(db_path: str):
    """
    Creates the article_analysis table if it doesn't exist.

    Parameters:
    db_path (str): The file path to the SQLite database.

    Returns:
    None
    """
    create_table_query = """
        CREATE TABLE IF NOT EXISTS article_analysis (
            title TEXT,
            article_text TEXT,
            sentiment TEXT,
            polarity REAL,
            subjectivity REAL,
            coherence REAL,
            topics TEXT
        )
    """
    execute_query_with_management(db_path, create_table_query)


def insert_article_analysis(db_path: str, results: list):
    """
    Inserts article analysis results into the article_analysis table.

    Parameters:
    db_path (str): The file path to the SQLite database.
    results (list): The analysis results to be inserted.

    Returns:
    None
    """
    insert_query = """
        INSERT INTO article_analysis (
            title
            , article_text
            , sentiment
            , polarity
            , subjectivity
            , coherence
            , topics)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    execute_query_with_management(db_path, insert_query, results, many=True)


def get_article_analysis_topics_by_sentiment(db_path: str, sentiment):
    """
    Retrieves article analysis topics by sentiment.

    Parameters:
    db_path (str): The file path to the SQLite database.
    sentiment (str): The sentiment to filter by.

    Returns:
    list: The retrieved topics.
    """
    return execute_query_with_management(
        db_path,
        "SELECT title, article_text, topics FROM article_analysis WHERE sentiment = ?",
        (sentiment,),
        fetch=True,
    )


def get_articles(db_path: str):
    """
    Retrieves articles from the database.

    Parameters:
    db_path (str): The file path to the SQLite database.

    Returns:
    list: The retrieved articles.
    """
    return execute_query_with_management(
        db_path, "SELECT Title, Article_Text FROM articles", fetch=True
    )


def get_subjectivity_distribution(db_path: str):
    """
    Retrieves the subjectivity distribution from the database.

    Parameters:
    db_path (str): The file path to the SQLite database.

    Returns:
    list: The subjectivity scores.
    """
    return execute_query_with_management(
        db_path, "SELECT subjectivity FROM article_analysis", fetch=True
    )


def get_objective_articles(db_path: str, threshold=0.5):
    """
    Retrieves objective articles from the database.

    Parameters:
    db_path (str): The file path to the SQLite database.
    threshold (float): The subjectivity threshold to filter by.

    Returns:
    list: The retrieved objective articles.
    """
    return execute_query_with_management(
        db_path,
        "SELECT title FROM article_analysis WHERE subjectivity < ?",
        (threshold,),
        fetch=True,
    )


def get_subjective_articles(db_path: str, threshold=0.5):
    """
    Retrieves subjective articles from the database.

    Parameters:
    db_path (str): The file path to the SQLite database.
    threshold (float): The subjectivity threshold to filter by.

    Returns:
    list: The retrieved subjective articles.
    """
    return execute_query_with_management(
        db_path,
        "SELECT title FROM article_analysis WHERE subjectivity >= ?",
        (threshold,),
        fetch=True,
    )


def correlate_subjectivity_sentiment(db_path: str):
    """
    Retrieves the correlation between subjectivity and sentiment.

    Parameters:
    db_path (str): The file path to the SQLite database.

    Returns:
    list: The correlation data.
    """
    return execute_query_with_management(
        db_path, "SELECT sentiment, subjectivity FROM article_analysis", fetch=True
    )


def get_articles_by_sentiment(db_path: str, sentiment):
    """
    Retrieves articles by sentiment from the database.

    Parameters:
    db_path (str): The file path to the SQLite database.
    sentiment (str): The sentiment to filter by.

    Returns:
    list: The retrieved articles.
    """
    return execute_query_with_management(
        db_path,
        "SELECT title, article_text FROM article_analysis WHERE sentiment = ?",
        (sentiment,),
        fetch=True,
    )


def create_analysis_table(db_path):
    """
    Creates the article_analysis table if it doesn't exist.

    Parameters:
    db_path (str): The file path to the SQLite database.

    Returns:
    None
    """
    execute_query_with_management(
        db_path,
        """CREATE TABLE IF NOT EXISTS article_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            article_text TEXT,
            topics TEXT,
            entities TEXT,
            c_v TEXT,
            u_mass TEXT,
            c_uci TEXT,
            c_npmi TEXT
        )""",
    )


def insert_analysis_data(
    db_path, title, article_text, topics, entities, coherence_score
):
    """
    Inserts analysis data into the article_topics table.

    Parameters:
    db_path (str): The file path to the SQLite database.
    title (str): The title of the article.
    article_text (str): The text of the article.
    topics (str): The topics of the article.
    entities (str): The entities in the article.
    coherence_score (dict): The coherence scores of the article.

    Returns:
    None
    """
    insert_query = """INSERT INTO article_topics (
        title, 
        article_text, 
        topics, 
        entities, 
        c_v, 
        u_mass, 
        c_uci, 
        c_npmi)"""
    execute_query_with_management(
        db_path,
        insert_query,
        (
            title,
            article_text,
            topics,
            entities,
            coherence_score["c_v"],
            coherence_score["u_mass"],
            coherence_score["c_uci"],
            coherence_score["c_npmi"],
        ),
    )


def drop_table(database_path, table_name):
    """
    Drops a table from the SQLite database.

    Parameters:
    database_path (str): The file path to the SQLite database.
    table_name (str): The name of the table to be dropped.

    Returns:
    None
    """
    try:
        execute_query_with_management(
            database_path, f"DROP TABLE IF EXISTS {table_name}"
        )
        print(f"Table '{table_name}' dropped successfully.")
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")


def save_analysis_data(
    db_path, title, article_text, topics, entities, coherence_scores
):
    """
    Saves analysis data to the database.

    Parameters:
    db_path (str): The file path to the SQLite database.
    title (str): The title of the article.
    article_text (str): The text of the article.
    topics (str): The topics of the article.
    entities (str): The entities in the article.
    coherence_scores (dict): The coherence scores of the article.

    Returns:
    None
    """
    create_analysis_table(db_path)
    insert_analysis_data(
        db_path, title, article_text, topics, entities, coherence_scores
    )


def delete_records_from_table(db_path: str, table: str, num_records: int):
    """
    Deletes a specified number of records from the articles table.

    Parameters:
    db_path (str): The file path to the SQLite database.
    num_records (int): The number of records to delete.

    Returns:
    None
    """
    delete_query = (
        f"DELETE FROM {table} WHERE rowid IN (SELECT rowid FROM articles LIMIT ?)"
    )
    execute_query_with_management(db_path, delete_query, (num_records,))
    print(f"{num_records} records deleted from the articles table.")
