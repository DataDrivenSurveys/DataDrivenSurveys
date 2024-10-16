"""Created on 2023-04-27 13:47.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

# __name__ = "ddsurveys"
__version__ = "1.0.0"
__license___ = "MIT License"
# __package__ = "ddsurveys"

# Set up custom loggers
import coloredlogs

from ddsurveys.data_providers import DataProvider
from ddsurveys.survey_platforms import SurveyPlatform

# We can override the builtin getLogger function with our own
# logging.getLogger = get_logger

coloredlogs.install()
