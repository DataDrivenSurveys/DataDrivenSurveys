"""Script to add Spacy models as project dependencies.

Use it to update the model versions after updating the Spacy library.

Usage:
    uv run scripts/update_spacy_models.py

Created on 2024-07-19 11:57.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

from spacy.cli.download import about, get_compatibility, get_model_filename, get_version, urljoin
from spacy.util import run_command
from tqdm import tqdm

models = [
    "ca_core_news_sm",
    "zh_core_web_sm",
    "hr_core_news_sm",
    "da_core_news_sm",
    "nl_core_news_sm",
    "en_core_web_sm",
    "fi_core_news_sm",
    "fr_core_news_sm",
    "de_core_news_sm",
    "el_core_news_sm",
    "it_core_news_sm",
    "ja_core_news_sm",
    "ko_core_news_sm",
    "lt_core_news_sm",
    "mk_core_news_sm",
    "nb_core_news_sm",
    "pl_core_news_sm",
    "pt_core_news_sm",
    "ro_core_news_sm",
    "ru_core_news_sm",
    "sl_core_news_sm",
    "es_core_news_sm",
    "sv_core_news_sm",
    "uk_core_news_sm",
]
compatibility = get_compatibility()


def update_spacy_models() -> None:
    """Function to install Spacy models as dependencies using uv.

    It recreates part of the Spacy CLI model installation process,
    but uses uv instead of pip.

    Returns:
        None
    """
    for model in tqdm(models, "Adding Spacy models"):
        version = get_version(model=model, comp=compatibility)

        filename = get_model_filename(model_name=model, version=version, sdist=False)

        base_url = about.__download_url__
        # urljoin requires that the path ends with /, or the last path part will be dropped
        if not base_url.endswith("/"):
            base_url = about.__download_url__ + "/"
        download_url = urljoin(base=base_url, url=filename)
        run_command(["uv", "add", "--quiet", download_url])


if __name__ == "__main__":
    update_spacy_models()
