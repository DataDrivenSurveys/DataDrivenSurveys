#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-07-05 13:03

@author: Lev Velykoivanenko (velykoivanenko.lev@gmail.com)
"""
import re

RE_SENTENCE_END = re.compile(r'[.!?]')


def count_words(note) -> int:
    return len(note.split(" "))


def count_sentences(note) -> int:
    return len(RE_SENTENCE_END.split(note)) - 1


if __name__ == "__main__":
    pass
