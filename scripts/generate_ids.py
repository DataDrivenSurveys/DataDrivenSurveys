#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-16 11:18

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
import argparse
import string
import random


CHARACTERS = string.ascii_letters + string.digits


def parse_args(args: list[str] = None):
    parser = argparse.ArgumentParser()

    return parser.parse_args(args)


def gen_string(length: int = 40, prefix: str = "", suffix: str = "", add_ellipsis: bool = True,
               char_set: str = CHARACTERS) -> str:
    s = "".join([random.choice(char_set) for _ in range(length)])

    if add_ellipsis:
        s = s[:max(len(s) // 2 - 2, 0)] + "..." + s[max(len(s) // 2 + 1, 0):]

    return prefix + s + suffix


if __name__ == "__main__":
    # r'^SV_[a-zA-Z0-9]{11,15}$'
    # Generate Qualtrics API Key string
    print(gen_string(40))

    # Generate Qualtrics Survey ID
    print(gen_string(15, "SV_"))

