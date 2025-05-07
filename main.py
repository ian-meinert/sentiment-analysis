"""Main module for running the machine learning pipeline to analyze news articles.
This module performs the following tasks:
1. Collects data from email attachments and saves it to an SQLite database.
2. Analyzes articles using a machine learning model and saves the analysis results to the database.
3. Retrieves articles with negative sentiment and their associated topics.
4. Analyzes the topics of the retrieved articles and exports the top topics to a CSV file.
Functions:
    main(): Main function to run the machine learning pipeline.
"""

import os
from pathlib import Path

from src.analysis.article_analyzer import ArticleAnalyzer
from src.analysis.topic_analysis import analyze_topics, export_top_topics_to_csv
from src.database.database_operations import get_article_analysis_topics_by_sentiment
from src.processors.data_collection import collect_the_data


def main():
    """
    Main function to perform the following tasks:
    1. Collect data from email attachments and save it to an SQLite database.
    2. Analyze articles and save the analysis data to the database.
    3. Collect negative sentiment articles, drop the article_text column, and export the top topics
       to a CSV file.
    Steps:
    - Set up the data folder and database path.
    - Collect data from email attachments.
    - Analyze articles using the ArticleAnalyzer class and save the results to the database.
    - Retrieve articles with negative sentiment and extract titles and topics.
    - Analyze the topics and export the top topics to a CSV file.
    Output:
    - Prints a message indicating that the analysis data has been saved to the database.
    - Prints a message indicating that the top topics have been saved to the specified CSV file.
    """
    data_folder = "data"
    db_path = os.path.join(data_folder, "articles.sqlite")

    # Collect the data from email attachments and save it to an SQLite database
    collect_the_data(data_folder)

    # Analyze articles
    model_path = os.path.join(Path(__file__).parent, "models")
    analyzer = ArticleAnalyzer(db_path, model_path)
    analyzer.analyze_and_save_articles()
    print("Analysis data has been saved to the database.")

    # Collect the negative sentiment articles and drop the article_text column
    articles = [
        (title, topics)
        for title, _, topics in get_article_analysis_topics_by_sentiment(
            db_path, sentiment="negative"
        )
    ]

    filename = "top_topics.csv"
    word_counts = analyze_topics(articles)
    export_top_topics_to_csv(
        word_counts=word_counts,
        articles=articles,
        top_n=25,
        data_folder=data_folder,
        filename=filename,
    )

    print(f"Top topics have been saved to '{filename}'.")


if __name__ == "__main__":
    main()
