"""
This module provides functions to remove similar article titles from a DataFrame.

Functions:
- remove_similar_titles(df: pd.DataFrame, threshold: int = 95) -> pd.DataFrame:
    Removes rows with similar article titles based on a similarity threshold.
        df (pd.DataFrame): DataFrame with 'Title' column.
        threshold (int, optional): Similarity threshold for removing titles. Default is 95.
"""

from fuzzywuzzy import fuzz


def remove_similar_titles(df, threshold=95):
    """
    Remove rows from a DataFrame that have similar titles based on a given similarity threshold.

    Args:
        df (pandas.DataFrame): The DataFrame containing a column named 'Title' with text data.
        threshold (int, optional): The similarity threshold (0-100) above which titles are
        considered similar. Defaults to 95.

    Returns:
        pandas.DataFrame: The DataFrame with similar titles removed.
    """
    to_drop = set()
    for i in range(len(df)):
        if i in to_drop:
            continue
        for j in range(i + 1, len(df)):
            if j in to_drop:
                continue
            similarity = fuzz.ratio(df.iloc[i]["Title"], df.iloc[j]["Title"])
            if similarity > threshold:
                to_drop.add(j)
    return df.drop(df.index[list(to_drop)])
