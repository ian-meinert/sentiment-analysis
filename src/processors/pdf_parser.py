import re

import pandas as pd
import pymupdf


def extract_objects_from_paragraphs(articles):
    """
    Extracts and collects objects between Heading 3 paragraphs in a list of paragraphs.
    This function searches through the paragraphs, identifies sections that match a specific
    pattern following a Heading 3 paragraph, and extracts relevant information to populate a
    DataFrame. The extracted information includes the title and the article text, which is
    collected until a "Back to Top" paragraph is encountered.
    Args:
        paragraphs (list): The list of paragraphs to be parsed.
    Returns:
        pd.DataFrame: A DataFrame containing the extracted data with columns "Title"
                      and "Article_Text".
    """
    df = pd.DataFrame(columns=["Title", "Article_Text"])
    data = {}

    for title, article_text in articles:
        data.update(
            {
                "Title": title,
                "Article_Text": " ".join(article_text),
            }
        )

        new_data_df = pd.DataFrame([data])
        df = pd.concat([new_data_df, df], ignore_index=True)

    return df


def get_content(paragraph_list, pattern):
    results = []
    title = None
    begin_reading = False

    for i, paragraph in enumerate(paragraph_list):
        combined_paragraph = paragraph
        # Combine current paragraph with the next two paragraphs
        if i + 1 < len(paragraph_list):
            combined_paragraph += " " + paragraph_list[i + 1]
        if i + 2 < len(paragraph_list):
            combined_paragraph += " " + paragraph_list[i + 2]

        # skip all content until the text "Full article text below:" is found
        if (
            "Full article text below" in paragraph
            or "Hyperlink to Above    Back to Top" in combined_paragraph
        ):
            begin_reading = True
            continue

        if begin_reading:
            end_of_article = "Back to Top" in paragraph

            # Check if the combined paragraph matches the pattern
            match = re.match(pattern, combined_paragraph.strip())

            if match and not title:
                # If a match is found, set the title
                title = match.group(0)  # Full matched string as title
                content = []  # Reset content for the new article
            # If we have a title, collect content until "Back to Top"
            elif not end_of_article and title and paragraph:
                content.append(paragraph)
            elif end_of_article and title:
                content_blob = " ".join(content).replace(title, "")
                article = (title, content_blob.strip())
                # append the article to the results list
                results.append(article)
                title = None
                continue

    return results


def parse_pdf(file_path):
    """
    Parses the PDF at the given file path, extracts relevant data, and returns it as a DataFrame.
    Args:
        file_path (str): The path to the PDF file to be parsed.
    Returns:
        pd.DataFrame: The DataFrame containing the extracted data.
    """
    # Define the regex pattern for matching titles

    pattern = (
        r"(\d+\.\d+) - (.+?): (.+) \((\d{1,2}\s(?:[A-Za-z]+))"
        r",( [\w ,-]+)?( \d+.?\w+ uvm;)?( [\w ,-]+)?\)"
    )
    articles = None

    # Use the 'with' statement to open the PDF file
    with pymupdf.open(file_path) as pdf_document:
        paragraphs = ""
        paragraph_list = []

        # Iterate through each page
        for _, page in enumerate(pdf_document):
            # Extract text from the page
            paragraphs += page.get_text()
            # Split the text into individual paragraphs
            # paragraph_list.append(paragraphs.split("\n"))
            # # Iterate through the paragraphs to find matches
            # articles = get_content(paragraph_list, pattern)

        paragraph_list = paragraphs.split("\n")
        articles = get_content(paragraph_list, pattern)

    result = extract_objects_from_paragraphs(articles[:-1])

    return result
