#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-07-05 13:03

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
import re

RE_SENTENCE_END = re.compile(r'[.!?。？！]')
RE_PARAGRAPH = re.compile(r'(?:\r?\n)+')


def count_words(text) -> int:
    return len(text.split(" "))


def count_sentences(text) -> int:
    return len(RE_SENTENCE_END.split(text)) - 1


def count_paragraphs(text) -> int:
    return len([s for s in RE_PARAGRAPH.split(text) if len(s.strip()) > 0])


if __name__ == "__main__":
    pass
