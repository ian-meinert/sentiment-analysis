"""
This module provides functions for setting up file directories and collecting data by processing
email attachments, cleaning the data, and saving it to an SQLite database.
Functions:
- setup_file_directories(data_folder, attachments_folder, emails_folder):
    Sets up the necessary file directories for data, attachments, and emails.
- collect_the_data(data_folder="data", attachments_folder="attachments", emails_folder="emails"):
    Collects data by processing email attachments, cleaning the data, and saving it to an SQLite
    database.
"""

import os

from ..database.database_operations import save_to_sqlite
from .data_cleaning import clean_article_data_from
from .email_processing import process_email_attachments


def setup_file_directories(data_folder, attachments_folder, emails_folder):
    """
    Sets up the necessary file directories for data, attachments, and emails.

    Parameters:
        data_folder (str): The main data folder.
        attachments_folder (str): The folder for storing attachments.
        emails_folder (str): The folder for storing emails.

    Returns:
        tuple: Paths to the data folder, attachments folder, and emails folder.
    """
    attachments = os.path.join(data_folder, attachments_folder)
    emails = os.path.join(data_folder, emails_folder)

    os.makedirs(data_folder, exist_ok=True)
    os.makedirs(attachments, exist_ok=True)
    os.makedirs(emails, exist_ok=True)
    return data_folder, attachments, emails


def collect_the_data(
    data_folder="data", attachments_folder="attachments", emails_folder="emails"
):
    """
    Collects data by processing email attachments, cleaning the data, and saving it to an SQLite
    database.

    Parameters:
        data_folder (str, optional):
            The main data folder. Default is "data".
        attachments_folder (str, optional):
            The folder for storing attachments. Default is "attachments".
        emails_folder (str, optional):
            The folder for storing emails. Default is "emails".
    """
    data, attachments, emails = setup_file_directories(
        data_folder, attachments_folder, emails_folder
    )
    attachments_path = os.path.join(os.getcwd(), attachments)

    # Process email attachments
    print("Processing email attachments...")
    df = process_email_attachments(emails, attachments_path)

    # Clean the DataFrame and perform any additional processing
    df = clean_article_data_from(df)
    # Save the DataFrame to sqlite for backup or further analysis

    db_file = os.path.join(data, "articles.sqlite")
    save_to_sqlite(df, db_file, table_name="articles", if_exists="append")
