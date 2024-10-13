"""Post install script for ddsurveys package.

Created on 2024-07-19 11:57.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
import importlib

from spacy.cli.download import download


def install_spacy_models() -> None:
    """Function to install Spacy models.

    Models are only installed if they are not already installed.
    The check for model availability is done by trying to import the model,
    which is much faster than loading the model.

    Returns:
        None
    """
    models = [
        'ca_core_news_sm',
        'zh_core_web_sm',
        'hr_core_news_sm',
        'da_core_news_sm',
        'nl_core_news_sm',
        'en_core_web_sm',
        'fi_core_news_sm',
        'fr_core_news_sm',
        'de_core_news_sm',
        'el_core_news_sm',
        'it_core_news_sm',
        'ja_core_news_sm',
        'ko_core_news_sm',
        'lt_core_news_sm',
        'mk_core_news_sm',
        'nb_core_news_sm',
        'pl_core_news_sm',
        'pt_core_news_sm',
        'ro_core_news_sm',
        'ru_core_news_sm',
        'sl_core_news_sm',
        'es_core_news_sm',
        'sv_core_news_sm',
        'uk_core_news_sm'
    ]

    for idx, model in enumerate(models):
        print(f"Progress: {idx + 1}/{len(models)} models")
        try:
            # print(f"Checking if spacy model '{model}' is installed...")
            importlib.import_module(model)
        except ModuleNotFoundError:
            # If the model is not installed, install it
            # print(f"Installing spacy model '{model}'...")
            download(model, False, False, "--quiet")


if __name__ == "__main__":
    install_spacy_models()
