"""
This module provides functions to clean article data from a DataFrame or an SQLite database.

Functions:
- clean_article_data_from(df: pd.DataFrame = None, sqlite_path: str = None) -> pd.DataFrame:
    Cleans article data from either a DataFrame or an SQLite database.
        df (pd.DataFrame, optional): DataFrame with 'Title' and 'Article_Text' columns.
        sqlite_path (str, optional): Path to the SQLite database file.
    Raises:
        ValueError: If both 'df' and 'sqlite_path' are provided or neither is provided.
"""

import pandas as pd

from ..database.connection import get_connection
from .duplicate_removal import remove_similar_titles


def _clean_from_sqlite(sqlite_path: str) -> pd.DataFrame:
    """
    Cleans the data from the SQLite database containing article titles and texts.

    Parameters:
    sq
    lite_path (str): Path to the SQLite database file.

    Returns:
    pd.DataFrame: Cleaned DataFrame with TF-IDF features added.
    """
    with get_connection(sqlite_path) as conn:
        df = pd.read_sql_query("SELECT * FROM articles", conn)
    return _clean_from_dataframe(df)


def _clean_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the given DataFrame containing article titles and texts.

    Parameters:
    df (pd.DataFrame): DataFrame with 'Title' and 'Article_Text' columns.

    Returns:
    pd.DataFrame: Cleaned DataFrame with TF-IDF features added.
    """
    # 1. Handling Missing Values
    df.fillna({"Title": "", "Article_Text": ""}, inplace=True)

    # 2. Removing Duplicates
    df.drop_duplicates(inplace=True)
    df = remove_similar_titles(df)

    # 3. Text Data Cleaning
    df["Article_Text"] = df["Article_Text"].str.replace(r"[^\w\s]", "", regex=True)

    return df


def clean_article_data_from(
    df: pd.DataFrame = None, sqlite_path: str = None
) -> pd.DataFrame:
    """
    Cleans article data from either a DataFrame or an SQLite database.
    This function takes either a pandas DataFrame or a path to an SQLite database,
    but not both, and cleans the article data accordingly.

    Parameters:
    df (pd.DataFrame, optional): The DataFrame containing the article data to be cleaned.
    sqlite_path (str, optional): The file path to the SQLite database containing the article
        data to be cleaned.

    Returns:
    pd.DataFrame: A DataFrame containing the cleaned article data.

    Raises:
    ValueError: If both 'df' and 'sqlite_path' are provided, or if neither is provided.
    """
    if df is not None and sqlite_path is not None:
        raise ValueError("Only one of 'df' or 'sqlite_path' should be provided.")
    if df is not None:
        return _clean_from_dataframe(df)
    if sqlite_path is not None:
        return _clean_from_sqlite(sqlite_path)
    raise ValueError("At least one parameter ('df' or 'sqlite_path') must be provided.")
