# Data-Driven Surveys Python Library

A platform supporting the creation of data-driven surveys.

## Usage

To use the Qualtrics API, you can set the QUALTRICS_API_TOKEN environment variable equal to the Qualtrics API token:
```bash
export QUALTRICS_API_TOKEN="Token"
```

Alternatively, when instantiating Qualtrics API related classes, you can pass it as the `api_token` parameter. For example:

```python
from survey_platforms.qualtrics import SurveysAPI

surveys_api = SurveysAPI(api_token="Token")
```
