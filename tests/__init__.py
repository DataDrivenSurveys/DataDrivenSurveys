#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-04-27 13:51

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

import json
from os import PathLike
from pathlib import Path
from typing import Iterator, Mapping

CURRENT_DIR = Path(__file__).resolve().parent


class TestsConfig(Mapping):
    _config: dict = {}

    def __init__(self, config_path: PathLike = None):
        if config_path is None:
            config_path = CURRENT_DIR.joinpath("test_config.json")
        self.config_path = config_path

    @property
    def config(self) -> dict:
        return self.__class__._config

    @config.setter
    def config(self, value: dict) -> None:
        if len(self.__class__._config) == 0:
            self.__class__._config = value
        else:
            raise ValueError("Tests configuration is already loaded.")

    def save_config(self) -> None:
        """
        Saves the tests configuration file.
        """
        with open(CURRENT_DIR.joinpath("test_config.json"), "w") as f:
            json.dump(self.config, f)

    def load_config(self) -> None:
        """
        Loads the tests configuration file.

        Returns:
            A dictionary containing the configuration.
        """
        with open(CURRENT_DIR.joinpath("test_config.json"), "r") as f:
            self.config = json.load(f)

    def __len__(self) -> int:
        return len(self.config)

    def __iter__(self) -> Iterator:
        return iter(self.config)

    def __contains__(self, item) -> None:
        return item in self._config

    def __getitem__(self, item) -> None:
        return self.config[item]

    def __setitem__(self, key, value) -> None:
        self.config[key] = value

    def __delitem__(self, key) -> None:
        del self.config[key]

    def __str__(self) -> str:
        return str(self.config)

    def __del__(self) -> None:
        """
        Saves the tests configuration file when the object is destroyed.

        Returns:

        """
        self.save_config()


# tests_config = TestsConfig()
