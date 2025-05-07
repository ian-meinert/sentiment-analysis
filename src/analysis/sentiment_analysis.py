"""
Module: sentiment_analysis
This module provides the TopicExtractor class for extracting topics from text based on sentiment
analysis.
Classes:
    TopicExtractor: A class to extract topics from text based on sentiment analysis.
"""

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

# Ensure stopwords and VADER lexicon are downloaded
nltk.download("stopwords")
nltk.download("vader_lexicon")


class TopicExtractor:
    """
    A class to extract topics from text based on sentiment analysis.

    Attributes:
        text (str): The text to analyze.
        sentiment_analyzer (SentimentIntensityAnalyzer): The sentiment analyzer.
        negative_words (list): A list of identified negative words.
    """

    def __init__(self, text):
        """
        Initializes the TopicExtractor with the given text.

        Args:
            text (str): The text to analyze.
        """
        self.text = text
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.negative_words = None

    def identify_negative_words(self):
        """
        Identifies negative words in the text.

        Returns:
            list: A list of negative words.
        """
        words = word_tokenize(self.text)
        negative_words = [
            word
            for word in words
            if self.sentiment_analyzer.polarity_scores(word)["compound"] <= -0.5
        ]
        self.negative_words = negative_words
        return self.negative_words

    def run(self):
        """
        Runs the topic extraction process.

        Returns:
            None
        """
        self.negative_words = self.identify_negative_words()
