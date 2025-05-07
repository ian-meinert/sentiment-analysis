"""
Module: entity_extraction
This module provides a function to extract named entities from text using spaCy.
Functions:
    extract_entities(text): Extracts named entities from the given text.
"""

import spacy

nlp = spacy.load("en_core_web_lg")


def extract_entities(text):
    """
    Extracts named entities from the given text.

    Args:
        text (str): The text to analyze.

    Returns:
        list: A list of tuples containing entity text and label.
    """
    doc = nlp(text)
    entities = [(entity.text, entity.label_) for entity in doc.ents]
    return entities
