"""Module: article_analyzer
This module provides the ArticleAnalyzer class, which is used to analyze articles for sentiment,
coherence, key phrases, and VA facilities mentions. It also provides methods to summarize articles
and save analysis results to a database.
Classes:
    ArticleAnalyzer: A class to perform various analyses on articles, including sentiment analysis,
    coherence calculation, key phrase extraction, and VA facilities identification.
Functions:
    get_pipeline(task, model_name, model_path):
        Returns a pipeline for the specified task and model.
    initialize_models():
        Initializes the sentiment analysis, summarization, and key phrase extraction models.
    __init__(db_path, model_path):
        Initializes the ArticleAnalyzer with the specified database and model paths.
    analyze_bias(text):
        Analyzes the bias of the given text, returning the average polarity and subjectivity scores.
    calculate_coherence(text):
        Calculates the coherence score of the given text based on cosine similarity of TF-IDF
        vectors.
    detailed_sentiment_analysis():
        Performs detailed sentiment analysis on articles from the database and returns the results.
    analyze_and_save_articles():
        Analyzes articles and saves the results to the database.
    extract_key_phrases(text):
        Extracts key phrases from the given text using a named entity recognition model.
    identify_va_facilities(text):
        Identifies VA facilities mentioned in the given text.
    summarize_article(text):
        Summarizes the given text using a summarization model.
    get_article_analysis_topics_by_sentiment(sentiment):
        Retrieves article analysis topics by sentiment from the database.
    analyze_article(text):
        Analyzes the given text for key phrases, VA facilities, and provides a summary.
"""

import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

from ..database.database_operations import (
    create_article_analysis_table,
    get_article_analysis_topics_by_sentiment,
    get_articles,
    insert_article_analysis,
)
from .sentiment_analysis import TopicExtractor


class ArticleAnalyzer:
    """ArticleAnalyzer class for analyzing news articles.
    Attributes:
        SENTIMENT_MODEL (str): The model name for sentiment analysis.
        SUMMARIZATION_MODEL (str): The model name for summarization.
        KEY_PHRASE_MODEL (str): The model name for key phrase extraction.
        model_path (str): The path to save/load models.
        db_path (str): The path to the database.
        va_facilities (list): List of VA facilities to identify in the text.
        max_length (int): Maximum input length for the model.
    Methods:
        get_pipeline(task, model_name, model_path):
            Get or download the pipeline for a specific task and model.
        initialize_models():
            Initialize the sentiment analysis, summarization, and key phrase extraction models.
        __init__(db_path, model_path):
            Initialize the ArticleAnalyzer with database and model paths.
        analyze_bias(text):
            Analyze the bias of the given text and return average polarity and subjectivity.
        calculate_coherence(text):
            Calculate the coherence score of the given text based on cosine similarity of TF-IDF
            vectors.
        detailed_sentiment_analysis():
            Perform detailed sentiment analysis on articles from the database and return the
            results.
        analyze_and_save_articles():
            Analyze articles and save the results to the database.
        extract_key_phrases(text):
            Extract key phrases from the given text using the key phrase extraction model.
        identify_va_facilities(text):
            Identify VA facilities mentioned in the given text.
        summarize_article(text):
            Summarize the given text using the summarization model.
        get_article_analysis_topics_by_sentiment(sentiment):
            Get article analysis topics filtered by sentiment from the database.
        analyze_article(text):
            Analyze the given article text and return a summary, key phrases, VA facilities, and key
            phrases discussed.
    """

    SENTIMENT_MODEL = "siebert/sentiment-roberta-large-english"
    SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
    KEY_PHRASE_MODEL = "dbmdz/bert-large-cased-finetuned-conll03-english"

    def get_pipeline(self, task, model_name, model_path):
        """
        Get or download the pipeline for a specific task and model.

        Args:
            task (str): The task for the pipeline (e.g., 'sentiment-analysis').
            model_name (str): The name of the model.
            model_path (str): The path to save/load the model.

        Returns:
            Pipeline: The loaded pipeline.
        """
        try:
            # Check if the model is available locally
            pipe = pipeline(task, model=model_path)
        except OSError:
            # If not, download the model to the specified path
            print(f"Downloading model {model_name} to {model_path}")
            pipe = pipeline(task, model=model_name)
            pipe.save_pretrained(model_path)

        return pipe

    def initialize_models(self):
        """
        Initialize the sentiment analysis, summarization, and key phrase extraction models.

        Returns:
            None
        """
        sentiment_model_path = os.path.join(self.model_path, "siebert")
        summarization_model_path = os.path.join(self.model_path, "facebook")
        key_phrase_model_path = os.path.join(self.model_path, "dbmdz")

        self.sentiment_analyzer = self.get_pipeline(
            "sentiment-analysis", self.SENTIMENT_MODEL, sentiment_model_path
        )
        self.summarizer = self.get_pipeline(
            "summarization", self.SUMMARIZATION_MODEL, summarization_model_path
        )

        self.key_phrase_extractor = self.get_pipeline(
            "ner", self.KEY_PHRASE_MODEL, key_phrase_model_path
        )

    def __init__(self, db_path, model_path):
        """
        Initialize the ArticleAnalyzer with database and model paths.

        Args:
            db_path (str): The path to the database.
            model_path (str): The path to save/load models.
        """
        self.model_path = model_path
        self.initialize_models()
        self.db_path = db_path
        self.va_facilities = [
            "VA Medical Center",
            "VA Hospital",
            "Veterans Affairs",
            "VA Clinic",
        ]  # Add more as needed
        self.max_length = 512  # Maximum input length for the model

    def analyze_bias(self, text):
        """
        Analyze the bias of the given text and return average polarity and subjectivity.

        Args:
            text (str): The text to analyze.

        Returns:
            tuple: A tuple containing average polarity and subjectivity scores.
        """
        # Split the text into chunks of max_length
        chunks = [
            text[i : i + self.max_length] for i in range(0, len(text), self.max_length)
        ]
        polarity_scores = []
        subjectivity_scores = []

        for chunk in chunks:
            result = self.sentiment_analyzer(chunk)[0]
            sentiment = result["label"]
            score = result["score"]
            polarity = score if sentiment == "POSITIVE" else -score
            # Normalize polarity to avoid extreme values
            polarity = max(min(polarity, 0.5), -0.5)
            subjectivity = 1 - score  # Simplified assumption
            polarity_scores.append(polarity)
            subjectivity_scores.append(subjectivity)

        # Aggregate the results
        avg_polarity = sum(polarity_scores) / len(polarity_scores)
        avg_subjectivity = sum(subjectivity_scores) / len(subjectivity_scores)
        return avg_polarity, avg_subjectivity

    def calculate_coherence(self, text):
        """
        Calculate the coherence score of a given text.
        The coherence score is calculated based on the cosine similarity
        between the TF-IDF vectors of the sentences in the text.
        Args:
            text (str): The input text to calculate coherence for.
        Returns:
            float: The coherence score of the text. A score of 1.0 indicates
                   perfect coherence (single sentence).
        """
        sentences = text.split(".")
        if len(sentences) < 2:
            return 1.0  # Single sentence, coherence is perfect

        vectorizer = TfidfVectorizer().fit_transform(sentences)
        vectors = vectorizer.toarray()
        cosine_matrix = cosine_similarity(vectors)
        coherence_score = cosine_matrix.mean()
        return coherence_score

    def detailed_sentiment_analysis(self):
        """
        Perform detailed sentiment analysis on articles from the database and return the results.

        Returns:
            list: A list of tuples containing detailed sentiment analysis results.
        """
        articles = get_articles(self.db_path)
        detailed_results = []
        for title, text in articles:
            topics = ""
            polarity, subjectivity = self.analyze_bias(text)
            coherence = self.calculate_coherence(text)
            if polarity > 0:
                sentiment = "positive"
            elif polarity < 0:
                sentiment = "negative"
                extractor = TopicExtractor(text)
                extractor.run()
                topics = ", ".join(extractor.negative_words)
            else:
                sentiment = "neutral"
            detailed_results.append(
                (title, text, sentiment, polarity, subjectivity, coherence, topics)
            )
        return detailed_results

    def analyze_and_save_articles(self):
        """
        Analyze articles and save the results to the database.

        Returns:
            None
        """
        results = self.detailed_sentiment_analysis()
        create_article_analysis_table(self.db_path)
        insert_article_analysis(self.db_path, results)

    def extract_key_phrases(self, text):
        """
        Extract key phrases from the given text using the key phrase extraction model.

        Args:
            text (str): The text to analyze.

        Returns:
            list: A list of extracted key phrases.
        """
        key_phrases = self.key_phrase_extractor(text)
        return [phrase["word"] for phrase in key_phrases]

    def identify_va_facilities(self, text):
        """
        Identify VA facilities mentioned in the given text.

        Args:
            text (str): The text to analyze.

        Returns:
            list: A list of identified VA facilities.
        """
        facilities = [facility for facility in self.va_facilities if facility in text]
        return facilities

    def summarize_article(self, text):
        """
        Summarize the given text using the summarization model.

        Args:
            text (str): The text to summarize.

        Returns:
            str: The summary of the text.
        """
        summary = self.summarizer(text, max_length=150, min_length=30, do_sample=False)
        return summary[0]["summary_text"]

    def get_article_analysis_topics_by_sentiment(self, sentiment):
        """
        Get article analysis topics filtered by sentiment from the database.

        Args:
            sentiment (str): The sentiment to filter by.

        Returns:
            list: A list of topics filtered by sentiment.
        """
        return get_article_analysis_topics_by_sentiment(self.db_path, sentiment)

    def analyze_article(self, text):
        """
        Analyze the given article text and return a summary, key phrases, VA facilities, and key
        phrases discussed.

        Args:
            text (str): The text to analyze.

        Returns:
            dict: A dictionary containing the analysis results.
        """
        key_phrases = [
            "PACT",
            "MISSION Act",
            "burn pit",
            "toxic exposure",
            "mental health",
            "PTSD",
            "Veteran suicide",
            "military sexual trauma",
            "Disability benefits",
            "healthcare access",
            "Community Care",
        ]
        summary = self.summarize_article(text)
        extracted_key_phrases = self.extract_key_phrases(text)
        va_facilities = self.identify_va_facilities(text)
        combined_key_phrases = set(extracted_key_phrases + key_phrases)
        key_phrases_discussed = [
            phrase for phrase in combined_key_phrases if phrase.lower() in text.lower()
        ]
        return {
            "summary": summary,
            "key_phrases": extracted_key_phrases,
            "va_facilities": va_facilities,
            "key_phrases_discussed": key_phrases_discussed,
        }
