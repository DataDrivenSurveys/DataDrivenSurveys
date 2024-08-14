#!/usr/bin/env python3
"""Created on 2024-07-19 14:47.

@author: Lev Velykoivanenko (lev.velykoivanenko@gmail.com)
"""
import os

import lingua
from lingua import Language, LanguageDetectorBuilder

SPACY_MODEL_LANGUAGES = {
    Language.CATALAN, Language.CHINESE, Language.CROATIAN, Language.DUTCH, Language.ENGLISH,
    Language.FINNISH, Language.FRENCH, Language.GERMAN, Language.GREEK, Language.ITALIAN, Language.JAPANESE,
    Language.KOREAN, Language.LITHUANIAN, Language.MACEDONIAN, Language.BOKMAL, Language.POLISH,
    Language.PORTUGUESE, Language.ROMANIAN, Language.RUSSIAN, Language.SLOVENE, Language.SPANISH,
    Language.SWEDISH, Language.UKRAINIAN
}


class LanguageDetector:
    """Singleton class for LanguageDetector instance."""
    _instance = None

    _detector_builder: LanguageDetectorBuilder = LanguageDetectorBuilder.from_all_languages()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, preload_models: bool = True):
        if os.getenv("DDS_ENV", "").lower() == "production":
            # Always preload models in production environment to improve performance.
            preload_models = True

        if preload_models:
            self.detector_builder.with_preloaded_language_models()
        self.detector: lingua.LanguageDetector = self.detector_builder.build()

    @property
    def detector_builder(self) -> LanguageDetectorBuilder:
        return self.__class__._detector_builder

    @staticmethod
    def get_iso_639_code(language: Language) -> str:
        if language is None:
            return None
        return language.iso_code_639_1.name.lower()

    @staticmethod
    def get_language_from_iso_639_code(iso_code: str) -> Language:
        if iso_code is None:
            return None
        return Language.from_iso_code_639_1(getattr(lingua.IsoCode639_1, iso_code.upper()))

    def detect_language(self, text, min_value: float = 0.6) -> Language | None:
        """Detects the language of the given text using Lingua.
        This function assumes that the text contains only one language.

        Args:
            text: Text to detect the language of.
            min_value: Minimum confidence value to consider a language as detected. Default is 0.6.

        Returns:
            The detected language instance if confidence is above min_value, otherwise None.

        """
        results = self.detector.compute_language_confidence_values(text)
        if results[0].value >= min_value:
            return results[0].language
        return None


