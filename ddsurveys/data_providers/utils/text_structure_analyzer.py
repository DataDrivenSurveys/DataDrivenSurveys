#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-07-05 13:03

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
import os
import re
import traceback

import spacy
import importlib
import inspect
from abc import ABC, abstractmethod

from ...get_logger import get_logger
from .language_detector import LanguageDetector

logger = get_logger(__name__)

RE_SENTENCE_END = re.compile(r'[.!?。？！]')
RE_PARAGRAPH = re.compile(r'(?:\r?\n)+')


class TextStructureAnalyzer(ABC):
    RE_PARAGRAPH = re.compile(r'(?:\r?\n)+')

    @abstractmethod
    def count_words(self, text: str) -> int:
        ...

    @abstractmethod
    def count_sentences(self, text: str) -> int:
        ...

    @abstractmethod
    def count_paragraphs(self, text: str) -> int:
        ...

    @abstractmethod
    def analyze_text(self, text: str) -> tuple[int, int, int]:
        ...


class SimpleTextStructureAnalyzer(TextStructureAnalyzer):
    def count_words(self, text) -> int:
        return len(text.split(" "))

    def count_sentences(self, text) -> int:
        return len(RE_SENTENCE_END.split(text)) - 1

    def count_paragraphs(self, text) -> int:
        return len([s for s in RE_PARAGRAPH.split(text) if len(s.strip()) > 0])

    def analyze_text(self, text: str) -> tuple[int, int, int]:
        return self.count_words(text), self.count_sentences(text), self.count_paragraphs(text)


class SpacyTextStructureAnalyzer(TextStructureAnalyzer):
    working_models = {}

    standard_models = {}
    external_models = {}

    failed_standard_models = set()

    available_external_models = {
        'ca': 'ca_core_news_sm',
        'zh': 'zh_core_web_sm',
        'hr': 'hr_core_news_sm',
        'da': 'da_core_news_sm',
        'nl': 'nl_core_news_sm',
        'en': 'en_core_web_sm',
        None: 'en_core_web_sm',
        'fi': 'fi_core_news_sm',
        'fr': 'fr_core_news_sm',
        'de': 'de_core_news_sm',
        'el': 'el_core_news_sm',
        'it': 'it_core_news_sm',
        'ja': 'ja_core_news_sm',
        'ko': 'ko_core_news_sm',
        'lt': 'lt_core_news_sm',
        'mk': 'mk_core_news_sm',
        'nb': 'nb_core_news_sm',
        'pl': 'pl_core_news_sm',
        'pt': 'pt_core_news_sm',
        'ro': 'ro_core_news_sm',
        'ru': 'ru_core_news_sm',
        'sl': 'sl_core_news_sm',
        'es': 'es_core_news_sm',
        'sv': 'sv_core_news_sm',
        'uk': 'uk_core_news_sm',
    }

    to_preload = (
        "en",
        "zh"
    )

    def __init__(self, prefer_external: bool = False, preload_models: bool = True) -> None:
        self.text: str = None
        self._doc: spacy.language.Doc = None
        self.language_detector = LanguageDetector(preload_models=preload_models)
        self.simple_analyzer = SimpleTextStructureAnalyzer()
        self.prefer_external = prefer_external

        if os.getenv("DDS_ENV", "").lower() == "production":
            preload_models = True

        if preload_models:
            # Preload models for the most spoken languages
            for model_name in self.__class__.to_preload:
                self.get_model(model_name, prefer_external)

            self.get_model(None)

    @property
    def doc(self) -> spacy.language.Doc:
        return self._doc

    @doc.setter
    def doc(self, value: spacy.language.Doc) -> None:
        if isinstance(value, str):
            self._ensure_doc(value)
        elif isinstance(value, spacy.language.Doc):
            self._doc = value
        else:
            raise TypeError(f"value must be a string or a spaCy Doc object. Received: {value} of type {type(value).__name__}")

    @classmethod
    def get_model(cls, language: str, prefer_external: bool = False) -> spacy.Language:
        if language in cls.working_models:
            return cls.working_models[language]

        orig_language = language
        if language is None:
            language = "en"  # Default to English if no language provided

        if language in cls.external_models:
            return cls.external_models[language]
        elif language in cls.standard_models:
            return cls.standard_models[language]

        nlp = None
        if not (prefer_external and language in cls.external_models):
            nlp = cls.get_standard_model(language)

        if nlp is None:
            nlp = cls.get_external_model(language)

        cls.working_models[language] = nlp

        if orig_language != language:
            cls.working_models[orig_language] = nlp

        return nlp

    @classmethod
    def get_standard_model(cls, language: str) -> spacy.Language | None:
        if language in cls.failed_standard_models:
            return None

        if language not in cls.standard_models:
            language_object = LanguageDetector.get_language_from_iso_639_code(language)
            language_name = language_object.name[0] + language_object.name[1:].lower()
            module = importlib.import_module(f"spacy.lang.{language}")
            nlp: spacy.Language = getattr(module, language_name)(enable=["sentencizer"])
            nlp.add_pipe('sentencizer')

            try:
                nlp("abcdefghijklmnopqrstuvwxyz")
            except Exception as e:
                logger.error(f"Failed to load standard Spacy model for language {language}: {e}")
                logger.debug(traceback.format_exc())
                cls.failed_standard_models.add(language)
                return None

            cls.standard_models[language] = nlp
        return cls.standard_models[language]

    @classmethod
    def get_external_model(cls, language: str) -> spacy.Language:
        if language not in cls.external_models:
            nlp = spacy.load(cls.available_external_models[language], enable=["sentencizer"])
            nlp.add_pipe('sentencizer')
            cls.external_models[language] = nlp
        return cls.external_models[language]

    @classmethod
    def load_all_working_models(cls):
        module = importlib.import_module("spacy.lang")
        for name, obj in inspect.getmembers(module, inspect.ismodule):
            if len(name) == 2 and name not in cls.working_models:
                cls.get_model(name)

    @classmethod
    def load_all_standard_models(cls):
        module = importlib.import_module("spacy.lang")
        for name, obj in inspect.getmembers(module, inspect.ismodule):
            if len(name) == 2:
                nlp = cls.get_standard_model(name)
                try:
                    nlp("")
                except Exception as e:
                    logger.error(f"Failed to load standard Spacy model for language {name}: {e}")
                    logger.debug(traceback.format_exc())
                    del cls.standard_models[name]
                    cls.failed_standard_models.add(name)

    @classmethod
    def load_all_external_models(cls):
        for language in cls.available_external_models:
            cls.get_external_model(language)

    def make_doc(self, text: str) -> spacy.language.Doc:
        language = self.language_detector.get_iso_639_code(self.language_detector.detect_language(text))
        return self.get_model(language)(text)

    def _ensure_doc(self, text: str):
        if text != self.text:
            self.text = text
            self._doc = self.make_doc(text)

    def count_words(self, text: str) -> int:
        self._ensure_doc(text)
        return len([token for token in self._doc if not token.is_punct and not token.is_space])

    def count_sentences(self, text: str) -> int:
        self._ensure_doc(text)
        len(list(self._doc.sents))

    def count_paragraphs(self, text: str) -> int:
        return self.simple_analyzer.count_paragraphs(text)

    def analyze_text(self, text: str) -> tuple[int, int, int]:
        self._ensure_doc(text)
        word_count = len([token for token in self._doc if not token.is_punct and not token.is_space])
        sentence_count = len(list(self._doc.sents))
        paragraph_count = self.simple_analyzer.count_paragraphs(text)
        return word_count, sentence_count, paragraph_count


if __name__ == "__main__":
    pass
