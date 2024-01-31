#!/bin/fish

curl --request POST \
  --url https://fra1.qualtrics.com/API/v3/survey-definitions \
  --header 'Content-Type: application/json' \
  --header 'X-API-TOKEN: ' \
  --data '{
  "SurveyName": "api-creation-test-survey",
  "Language": "EN",
  "ProjectCategory": "CORE"
}'
