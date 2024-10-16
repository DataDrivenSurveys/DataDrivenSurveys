"""Created on 2023-05-23 14:07.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

__all__ = ["SurveyPlatform"]

from ddsurveys.dynamic_import import dynamic_import
from ddsurveys.survey_platforms.bases import SurveyPlatform

excluded_dynamic_load_modules = ("bases", "__init__", "_registration", "exceptions", "template", "template_oauth")

modules = dynamic_import(__file__, exclude_names=excluded_dynamic_load_modules, recursive=False)
