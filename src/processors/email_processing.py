"""
Processes email attachments by extracting data from .docx and .pdf files.

Args:
    email_dir (str): The directory containing the emails.
    attachments_dir (str): The directory where attachments are saved.

Returns:
    pd.DataFrame: A DataFrame containing the extracted data from .docx files.
                  If no attachments are found, returns an empty DataFrame.

Raises:
    FileNotFoundError: If the specified directories do not exist.
    Exception: For any other exceptions that occur during processing.

Notes:
    - The function first parses the emails to extract attachments and save them to the specified
        directory.
    - It then processes each attachment, extracting data from .docx files and concatenating it into
        a DataFrame.
    - .pdf files are parsed but their data is not included in the returned DataFrame.
"""

import os

import pandas as pd

from .document_parser import parse_document
from .extract_attachments import parse_from_path
from .pdf_parser import parse_pdf


def process_email_attachments(email_dir: str, attachments_dir: str) -> pd.DataFrame:
    """
    Processes email attachments by extracting data from .docx and .pdf files.
    Args:
        email_dir (str): The directory containing the emails.
        attachments_dir (str): The directory where attachments are saved.
    Returns:
        pd.DataFrame: A DataFrame containing the extracted data from .docx files.
                      If no attachments are found, returns an empty DataFrame.
    Raises:
        FileNotFoundError: If the specified directories do not exist.
        Exception: For any other exceptions that occur during processing.
    Notes:
        - The function first parses the emails to extract attachments and save them to the specified
            directory.
        - It then processes each attachment, extracting data from .docx files and concatenating it
            into a DataFrame.
        - .pdf files are parsed but their data is not included in the returned DataFrame.
    """
    data = pd.DataFrame()

    print("Extracting data from email attachments...")
    parse_from_path(path_in=email_dir, path_out=attachments_dir)

    if not os.path.isdir(attachments_dir):
        print("No attachments found.")
        return pd.DataFrame()

    for filename in os.listdir(attachments_dir):
        file_path = os.path.join(attachments_dir, filename)
        if filename.endswith(".docx"):
            doc_data = parse_document(file_path)
            print(f"Extracted data from {filename}")
            data = pd.concat([data, doc_data], ignore_index=True)
        elif filename.endswith(".pdf"):
            pdf_data = parse_pdf(file_path)
            print(f"Extracted data from {filename}")
            data = pd.concat([data, pdf_data], ignore_index=True)

    print(f"Total articles extracted: {len(data)}")
    return data
