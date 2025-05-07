"""
Module: topic_analysis
This module provides functions for analyzing topics in articles, including collecting negative
articles, analyzing topics, and exporting top topics to a CSV file.
Functions:
    collect_negative_articles(db_path): Collects articles with negative sentiment from the database.
    analyze_topics(articles): Analyzes topics from the collected articles.
    export_top_topics_to_csv(word_counts, articles, top_n, data_folder, filename): Exports the top
        topics to a CSV file.
    main(): Main function to collect articles, analyze topics, and export top topics to CSV.
"""

import csv
import os
import sqlite3
from collections import Counter

import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize

# Ensure necessary NLTK data is downloaded
nltk.download("averaged_perceptron_tagger")

# Define excluded topics
EXCLUDED_TOPICS = {
    "donald",
    "trump",
    "defense",
    "department",
    "va",
    "vas",
    "affairs",
    "veteran",
}


def collect_negative_articles(db_path):
    """
    Collects articles with negative sentiment from the database.

    Args:
        db_path (str): The path to the database.

    Returns:
        list: A list of tuples containing article titles and topics.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT title, topics FROM article_analysis WHERE sentiment = 'negative'"
    cursor.execute(query)
    articles = cursor.fetchall()
    conn.close()
    return articles


def analyze_topics(articles):
    """
    Analyzes topics from the collected articles.

    Args:
        articles (list): A list of tuples containing article titles and topics.

    Returns:
        Counter: A counter object with word counts of relevant topics.
    """
    ## Join topics from articles and tokenize
    all_topics = " ".join(topics for _, topics in articles)
    filtered_words = [
        word
        for word in word_tokenize(all_topics)
        if word.lower() not in EXCLUDED_TOPICS
    ]

    # Apply POS tagging
    pos_tags = pos_tag(filtered_words)

    # Define relevant parts of speech
    relevant_pos = [
        "NN",  # Nouns
        "VB",  # Verbs
        "RB",  # Adverbs
    ]

    # Filter for relevant nouns, verbs, and adjectives
    verbs_and_nouns = [word for word, pos in pos_tags if pos in relevant_pos]

    # Count occurrences of each word
    word_counts = Counter(verbs_and_nouns)

    return word_counts


def export_top_topics_to_csv(
    word_counts, articles, top_n=10, data_folder=None, filename="top_topics.csv"
):
    """
    Exports the top topics to a CSV file.

    Args:
        word_counts (Counter): A counter object with word counts of relevant topics.
        articles (list): A list of tuples containing article titles and topics.
        top_n (int): The number of top topics to export.
        data_folder (str): The folder to save the CSV file.
        filename (str): The name of the CSV file.

    Returns:
        None
    """
    # join the file path
    filepath = os.path.join(data_folder, filename)
    top_words = word_counts.most_common(top_n)
    top_titles_and_topics = {word: set() for word, _ in top_words}
    for word, _ in top_words:
        for title, topics in articles:
            if word in topics:
                top_titles_and_topics[word].add(title)

    with open(filepath, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Topic", "Titles"])
        for word, titles in top_titles_and_topics.items():
            writer.writerow([word, "\r\n".join(titles)])


def main():
    """
    Main function to collect articles, analyze topics, and export top topics to CSV.

    Returns:
        None
    """
    data_folder = "data"
    db_path = "data/articles.sqlite"
    articles = collect_negative_articles(db_path)
    word_counts = analyze_topics(articles)
    export_top_topics_to_csv(
        word_counts, articles, data_folder=data_folder, filename="top_topics.csv"
    )


if __name__ == "__main__":
    main()
