"""
Module: topic_modeling
This module provides functions for topic modeling using LDA, including tokenization,
dictionary creation, bag-of-words corpus creation, and coherence score calculation.
Functions:
    tokenize_text(article_text): Tokenizes the input text into words.
    create_dictionary(tokenized_text): Creates a dictionary representation of the tokenized text.
    create_bow_corpus(dictionary, tokenized_text): Converts tokenized text into a bag-of-words (BoW)
        corpus.
    perform_topic_modeling(bow_corpus, dictionary): Performs topic modeling using LDA.
    calculate_coherence_scores(tokenized_text, dictionary, lda_model): Calculates coherence scores
        for the LDA model.
    extract_entities_from_text(tokenized_text): Extracts entities from the tokenized text.
    perform_lda(tokenized_text): Performs LDA topic modeling on the tokenized text.
    print_topics(lda_model, num_words): Prints the topics from the LDA model.
"""

from gensim import corpora, models
from gensim.models.coherencemodel import CoherenceModel
from nltk.tokenize import word_tokenize

from .entity_extraction import extract_entities


def tokenize_text(article_text):
    """
    Tokenizes the input text into words.

    Args:
        article_text (str): The text of the article to tokenize.

    Returns:
        list: A list of tokenized words.
    """
    return word_tokenize(article_text)


def create_dictionary(tokenized_text):
    """
    Creates a dictionary representation of the tokenized text.

    Args:
        tokenized_text (list): A list of tokenized words.

    Returns:
        Dictionary: A Gensim dictionary object.
    """
    return corpora.Dictionary([tokenized_text])


def create_bow_corpus(dictionary, tokenized_text):
    """
    Converts tokenized text into a bag-of-words (BoW) corpus.

    Args:
        dictionary (Dictionary): A Gensim dictionary object.
        tokenized_text (list): A list of tokenized words.

    Returns:
        list: A list of BoW representations.
    """
    return [dictionary.doc2bow(tokenized_text)]


def perform_topic_modeling(bow_corpus, dictionary):
    """
    Performs topic modeling using LDA.

    Args:
        bow_corpus (list): A list of BoW representations.
        dictionary (Dictionary): A Gensim dictionary object.

    Returns:
        tuple: A tuple containing the LDA model and a string of topics.
    """
    lda_model = models.LdaModel(bow_corpus, num_topics=5, id2word=dictionary, passes=15)
    topics_list = lda_model.print_topics(num_words=4)
    topics = ", ".join([topic[1] for topic in topics_list])
    return lda_model, topics


def calculate_coherence_scores(tokenized_text, dictionary, lda_model):
    """
    Calculates coherence scores for the LDA model.

    Args:
        tokenized_text (list): A list of tokenized words.
        dictionary (Dictionary): A Gensim dictionary object.
        lda_model (LdaModel): A trained LDA model.

    Returns:
        dict: A dictionary of coherence scores.
    """
    coherence_scores = {}
    for coherence_type in ["c_v", "u_mass", "c_uci", "c_npmi"]:
        coherence_model_lda = CoherenceModel(
            model=lda_model,
            texts=[tokenized_text],
            dictionary=dictionary,
            coherence=coherence_type,
        )
        coherence_scores[coherence_type] = coherence_model_lda.get_coherence()

    return coherence_scores


def extract_entities_from_text(tokenized_text):
    """
    Extracts entities from the tokenized text.

    Args:
        tokenized_text (list): A list of tokenized words.

    Returns:
        str: A string of extracted entities.
    """
    entities_list = [extract_entities(text) for text in tokenized_text]
    flattened_entities_list = [
        entity for sublist in entities_list for entity in sublist
    ]
    entities = ", ".join([entity[0] for entity in flattened_entities_list])
    return entities


def perform_lda(tokenized_text):
    """
    Performs LDA topic modeling on the tokenized text.

    Args:
        tokenized_text (list): A list of tokenized words.

    Returns:
        LdaModel: A trained LDA model.
    """
    dictionary = corpora.Dictionary([tokenized_text])
    bow_corpus = [dictionary.doc2bow(tokenized_text)]
    lda_model = models.LdaModel(bow_corpus, num_topics=5, id2word=dictionary, passes=15)
    return lda_model


def print_topics(lda_model, num_words=4):
    """
    Prints the topics from the LDA model.

    Args:
        lda_model (LdaModel): A trained LDA model.
        num_words (int): The number of words per topic to print.

    Returns:
        list: A list of topics.
    """
    topics = lda_model.print_topics(num_words=num_words)
    return topics
