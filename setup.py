#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2020-04-22 11:01

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from setuptools import setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # Download the TextBlob corpora
        models = [
            "xx_ent_wiki_sm",
            "zh_core_web_sm",
            "fr_core_news_sm",
            "de_core_news_sm",
            "es_core_news_sm",
            "pt_core_news_sm",
            "ru_core_news_sm",
            "ja_core_news_sm",
            "ko_core_news_sm",
            "zh_core_web_trf"
        ]
        from spacy.cli.download import download
        for model in models:
            download(model)
        install.run(self)


setup(
    cmdclass={
        'install': PostInstallCommand,
    },
)
