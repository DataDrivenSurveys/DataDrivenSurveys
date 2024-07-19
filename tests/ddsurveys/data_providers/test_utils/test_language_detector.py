#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-07-19 14:54

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

import pytest
from .data import TEXTS


def test_language_detection():
    from ddsurveys.data_providers.utils.language_detector import LanguageDetector

    detector = LanguageDetector()
    for lang, text in TEXTS.items():
        if lang == "zh-tw":
            lang = "zh"
        assert detector.get_iso_639_code(detector.detect_language(text)) == lang
