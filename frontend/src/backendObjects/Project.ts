export type DataProviderType = "frontend" | "oauth" | "generic";

export type SurveyStatus = "active" | "inactive" | "unknown";

export interface Researcher {
  id: number;
  email: string;
  firstname: string;
  lastname: string;
}

export interface Collaborations {
  project_id: string;
  researcher: Researcher;
}

interface DataOrigin {
  documentation: string;
  endpoint?: string;
  method?: string;
}

namespace CV {
  export interface Attribute {
    attribute: string;
    category: string;
    data_origin: DataOrigin[];
    data_type: string;
    description: string;
    enabled: boolean;
    info: string;
    label: string;
    name: string;
    test_value: string;
    test_value_placeholder: string;
    unit: string;
  }

  export interface Filter {
    attr: string;
    operator: string;
    value: string;
  }

  export interface Selection {
    attr: string;
    operator: string;
  }
}

export interface CustomVariable {
  cv_attributes: CV.Attribute[];
  data_category: string;
  data_provider: string;
  filters: CV.Filter[];
  id: number;
  selection: CV.Selection;
  type: 'Custom';
  variable_name: string;
}

export interface DataProvider {
  data_provider_name: string;
  data_provider_type: DataProviderType;
  name: string;
}

export interface DataConnection {
  data_provider: DataProvider;
  data_provider_name: string;
  fields: {
    client_id?: string;
    client_secret?: string;
    project_id?: string;
    information?: string;
  };
  project_id: string;
}

export interface Distribution {
  id: number;
  url: string;
}

export interface Respondent {
  distribution: Distribution;
  id: string;
  project_id: string;
}

export interface SurveyPlatformFields {
  base_url: string;
  directory_id?: string;
  mailing_list_id?: string;
  survey_id: string;
  survey_name: string;
  survey_platform_api_key: string;
  survey_status: SurveyStatus;
}

export interface BuiltinVariable {
  category: string;
  data_origin: DataOrigin[];
  data_provider: string;
  data_type: string;
  description: string;
  enabled: boolean;
  id: number;
  index: number | null;
  info: string;
  is_indexed_variable: boolean;
  label: string;
  name: string;
  provider_type: DataProviderType;
  qualified_name: string;
  test_value: string;
  test_value_placeholder: string;
  type: 'Builtin';
  unit: string | null;
}

interface Project {
  collaborations: Collaborations[];
  creation_date: string;
  custom_variables: CustomVariable[];
  data_connections: DataConnection[];
  id: string;
  last_modified: string;
  last_synced: string | null;
  name: string;
  respondents: Respondent[];
  short_id: string;
  survey_platform_fields: SurveyPlatformFields;
  survey_platform_name: string;
  survey_status: string;
  variables: BuiltinVariable[];
}

export default Project;


const cv: CustomVariable = {
  "cv_attributes": [
    {
      "attribute": "duration",
      "category": "Activities",
      "data_origin": [],
      "data_type": "Number",
      "description": "The duration of the activity in seconds.",
      "enabled": true,
      "info": "The duration of the activity in seconds",
      "label": "Activity Duration",
      "name": "duration",
      "test_value": "",
      "test_value_placeholder": "100",
      "unit": "seconds"
    },
    {
      "attribute": "calories",
      "category": "Activities",
      "data_origin": [],
      "data_type": "Number",
      "description": "The number of calories burned during the activity in kcal.",
      "enabled": true,
      "info": "The number of calories burned during the activity",
      "label": "Calories Burned",
      "name": "calories",
      "test_value": "",
      "test_value_placeholder": "100",
      "unit": "kcal"
    },
    {
      "attribute": "originalStartTime",
      "category": "Activities",
      "data_origin": [],
      "data_type": "Date",
      "description": "The date of the activity.",
      "enabled": true,
      "info": "The date of the activity",
      "label": "Date",
      "name": "date",
      "test_value": "",
      "test_value_placeholder": "2023-01-10T12:00:00.000+02:00",
      "unit": ""
    },
    {
      "attribute": "distance",
      "category": "Activities",
      "data_origin": [],
      "data_type": "Number",
      "description": "The distance traveled during the activity in meters.",
      "enabled": true,
      "info": "The distance traveled during the activity",
      "label": "Distance",
      "name": "distance",
      "test_value": "",
      "test_value_placeholder": "100",
      "unit": "meters"
    },
    {
      "attribute": "activityName",
      "category": "Activities",
      "data_origin": [],
      "data_type": "Text",
      "description": "The type of the activity.",
      "enabled": true,
      "info": "The type of activity",
      "label": "Activity Type",
      "name": "type",
      "test_value": "",
      "test_value_placeholder": "Walk",
      "unit": ""
    }
  ],
  "data_category": "activities",
  "data_provider": "fitbit",
  "filters": [
    {
      "attr": "activityName",
      "operator": "regexp",
      "value": "run"
    },
    {
      "attr": "calories",
      "operator": "__gt__",
      "value": "100"
    },
    {
      "attr": "originalStartTime",
      "operator": "__lt__",
      "value": "2024-08-31T22:00:00.000Z"
    }
  ],
  "id": 16,
  "selection": {
    "attr": "distance",
    "operator": "min"
  },
  "type": "Custom",
  "variable_name": "run"
}


const temp: Project = {
  "collaborations": [
    {
      "project_id": "ab715443-3a2d-44c3-bcb9-7eb7bb88c7df",
      "researcher": {
        "email": "lev.velykoivanenko@unil.ch",
        "firstname": "Lev",
        "id": 1,
        "lastname": "Velykoivanenko"
      }
    }
  ],
  "creation_date": "Thu, 15 Aug 2024 11:34:02 GMT",
  "custom_variables": [
    {
      "cv_attributes": [
        {
          "attribute": "duration",
          "category": "Activities",
          "data_origin": [],
          "data_type": "Number",
          "description": "The duration of the activity in seconds.",
          "enabled": true,
          "info": "The duration of the activity in seconds",
          "label": "Activity Duration",
          "name": "duration",
          "test_value": "",
          "test_value_placeholder": "100",
          "unit": "seconds"
        },
        {
          "attribute": "calories",
          "category": "Activities",
          "data_origin": [],
          "data_type": "Number",
          "description": "The number of calories burned during the activity in kcal.",
          "enabled": true,
          "info": "The number of calories burned during the activity",
          "label": "Calories Burned",
          "name": "calories",
          "test_value": "",
          "test_value_placeholder": "100",
          "unit": "kcal"
        },
        {
          "attribute": "originalStartTime",
          "category": "Activities",
          "data_origin": [],
          "data_type": "Date",
          "description": "The date of the activity.",
          "enabled": true,
          "info": "The date of the activity",
          "label": "Date",
          "name": "date",
          "test_value": "",
          "test_value_placeholder": "2023-01-10T12:00:00.000+02:00",
          "unit": ""
        },
        {
          "attribute": "distance",
          "category": "Activities",
          "data_origin": [],
          "data_type": "Number",
          "description": "The distance traveled during the activity in meters.",
          "enabled": true,
          "info": "The distance traveled during the activity",
          "label": "Distance",
          "name": "distance",
          "test_value": "",
          "test_value_placeholder": "100",
          "unit": "meters"
        },
        {
          "attribute": "activityName",
          "category": "Activities",
          "data_origin": [],
          "data_type": "Text",
          "description": "The type of the activity.",
          "enabled": true,
          "info": "The type of activity",
          "label": "Activity Type",
          "name": "type",
          "test_value": "",
          "test_value_placeholder": "Walk",
          "unit": ""
        }
      ],
      "data_category": "activities",
      "data_provider": "fitbit",
      "filters": [
        {
          "attr": "activityName",
          "operator": "regexp",
          "value": "run"
        },
        {
          "attr": "calories",
          "operator": "__gt__",
          "value": "100"
        },
        {
          "attr": "originalStartTime",
          "operator": "__lt__",
          "value": "2024-08-31T22:00:00.000Z"
        }
      ],
      "id": 16,
      "selection": {
        "attr": "distance",
        "operator": "min"
      },
      "type": "Custom",
      "variable_name": "run"
    }
  ],
  "data_connections": [
    {
      "data_provider": {
        "data_provider_name": "fitbit",
        "data_provider_type": "oauth",
        "name": "Fitbit"
      },
      "data_provider_name": "fitbit",
      "fields": {
        "client_id": "23RYN2",
        "client_secret": "9469c10a9ab2e7d69ad678d9f4b52482"
      },
      "project_id": "ab715443-3a2d-44c3-bcb9-7eb7bb88c7df"
    },
    {
      "data_provider": {
        "data_provider_name": "dds",
        "data_provider_type": "frontend",
        "name": "DDS"
      },
      "data_provider_name": "dds",
      "fields": {
        "information": ""
      },
      "project_id": "ab715443-3a2d-44c3-bcb9-7eb7bb88c7df"
    }
  ],
  "id": "ab715443-3a2d-44c3-bcb9-7eb7bb88c7df",
  "last_modified": "Sat, 14 Sep 2024 15:22:50 GMT",
  "last_synced": "Thu, 12 Sep 2024 14:01:37 GMT",
  "name": "Fitbit Usage Study",
  "respondents": [
    {
      "distribution": {
        "id": 11,
        "url": "https://ulausannebusiness.eu.qualtrics.com/jfe/form/SV_cXYa9YcvWpiBGN8?Q_CHL=gl&Q_DL=EMD_9erqHnUEtOIO7wR_cXYa9YcvWpiBGN8_CGC_MalwE2WhW2TeQMr&_g_=g"
      },
      "id": "db9671b8-b755-4256-9691-2d1dc179aec4",
      "project_id": "ab715443-3a2d-44c3-bcb9-7eb7bb88c7df"
    }
  ],
  "short_id": "527126776468504580",
  "survey_platform_fields": {
    "base_url": "https://ulausannebusiness.eu.qualtrics.com",
    "directory_id": "POOL_Uu3EWHayDrQRZYd",
    "mailing_list_id": "CG_33ya474vhCDzl0V",
    "survey_id": "SV_cXYa9YcvWpiBGN8",
    "survey_name": "Fitbit Usage Study",
    "survey_platform_api_key": "kgxfjHFUfSbkH8xHYFSP7oQqE7hS8A3mDva18oLd",
    "survey_status": "active"
  },
  "survey_platform_name": "qualtrics",
  "survey_status": "unknown",
  "variables": [
    {
      "category": "FrontendActivity",
      "data_origin": [
        {
          "documentation": "Monitored by the frontend application."
        }
      ],
      "data_provider": "dds",
      "data_type": "Text",
      "description": "Indicates whether the respondent has accessed the transparency table.",
      "enabled": true,
      "id": 0,
      "index": null,
      "info": "This variable reflects access to the transparency table, set to 'Yes' if accessed and 'No' otherwise.",
      "is_indexed_variable": false,
      "label": "Open Transparency Table",
      "name": "open_transparency_table",
      "provider_type": "frontend",
      "qualified_name": "dds.dds.builtin.frontendactivity.open_transparency_table",
      "test_value": "Yes",
      "test_value_placeholder": "Yes",
      "type": "Builtin",
      "unit": null
    },
    {
      "category": "Activities",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
          "method": "activities_frequent"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Text",
      "description": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, index 2 is the second most frequent activity, and so on.",
      "enabled": true,
      "id": 1,
      "index": 1,
      "info": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, ",
      "is_indexed_variable": true,
      "label": "Activities by Frequency",
      "name": "by_frequency",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activities.by_frequency1",
      "test_value": "Walk",
      "test_value_placeholder": "Walk",
      "type": "Builtin",
      "unit": null
    },
    {
      "category": "Activities",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
          "method": "activities_frequent"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Text",
      "description": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, index 2 is the second most frequent activity, and so on.",
      "enabled": true,
      "id": 2,
      "index": 2,
      "info": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, ",
      "is_indexed_variable": true,
      "label": "Activities by Frequency",
      "name": "by_frequency",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activities.by_frequency2",
      "test_value": "Walk",
      "test_value_placeholder": "Walk",
      "type": "Builtin",
      "unit": null
    },
    {
      "category": "Activities",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
          "method": "activities_frequent"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Text",
      "description": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, index 2 is the second most frequent activity, and so on.",
      "enabled": false,
      "id": 3,
      "index": 3,
      "info": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, ",
      "is_indexed_variable": true,
      "label": "Activities by Frequency",
      "name": "by_frequency",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activities.by_frequency3",
      "test_value": "Walk",
      "test_value_placeholder": "Walk",
      "type": "Builtin",
      "unit": null
    },
    {
      "category": "Activities",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
          "method": "activities_frequent"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Text",
      "description": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, index 2 is the second most frequent activity, and so on.",
      "enabled": false,
      "id": 4,
      "index": 4,
      "info": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, ",
      "is_indexed_variable": true,
      "label": "Activities by Frequency",
      "name": "by_frequency",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activities.by_frequency4",
      "test_value": "Walk",
      "test_value_placeholder": "Walk",
      "type": "Builtin",
      "unit": null
    },
    {
      "category": "Activities",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
          "method": "activities_frequent"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Text",
      "description": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, index 2 is the second most frequent activity, and so on.",
      "enabled": false,
      "id": 5,
      "index": 5,
      "info": "Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, ",
      "is_indexed_variable": true,
      "label": "Activities by Frequency",
      "name": "by_frequency",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activities.by_frequency5",
      "test_value": "Walk",
      "test_value_placeholder": "Walk",
      "type": "Builtin",
      "unit": null
    },
    {
      "category": "Account",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
          "method": "user_profile"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Text",
      "description": "Account Created at Least 1 Year Ago.",
      "enabled": true,
      "id": 6,
      "index": null,
      "info": "This will be 'True' if the account was created at least 1 year ago, otherwise 'False'.",
      "is_indexed_variable": false,
      "label": "Account Created at Least 1 Year Ago",
      "name": "account_created_at_least_1_year_ago",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.account.account_created_at_least_1_year_ago",
      "test_value": "True",
      "test_value_placeholder": "True",
      "type": "Builtin",
      "unit": null
    },
    {
      "category": "Account",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
          "method": "user_profile"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Date",
      "description": "Date of account creation.",
      "enabled": false,
      "id": 7,
      "index": null,
      "info": "This will be the date that the respondent's Fitbit account was created. It will be in YYYY-MM-DD format.",
      "is_indexed_variable": false,
      "label": "Account Creation Date",
      "name": "creation_date",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.account.creation_date",
      "test_value": "2020-01-01",
      "test_value_placeholder": "2020-01-01",
      "type": "Builtin",
      "unit": null
    },
    {
      "category": "ActiveMinutes",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/[activityType]/date/[start-date]/[end-date].json",
          "method": ""
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Number",
      "description": "Average weekly active minutes from all sources (tracker and manual entry)",
      "enabled": true,
      "id": 8,
      "index": null,
      "info": "Average weekly active minutes from all sources (tracker and manual entry) over the last 6 months.",
      "is_indexed_variable": false,
      "label": "Average Weekly Active Minutes From All sources Last 6 Months",
      "name": "average_weekly_active_time_all_sources_last_6_months",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activeminutes.average_weekly_active_time_all_sources_last_6_months",
      "test_value": "120",
      "test_value_placeholder": "120",
      "type": "Builtin",
      "unit": "minutes"
    },
    {
      "category": "ActiveMinutes",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/[activityType]/date/[start-date]/[end-date].json",
          "method": ""
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Number",
      "description": "Average weekly active minutes only from a tracker",
      "enabled": true,
      "id": 9,
      "index": null,
      "info": "Average weekly active minutes only from a tracker over the last 6 months.",
      "is_indexed_variable": false,
      "label": "Average Weekly Active Minutes Only From A Tracker Last 6 Months",
      "name": "average_weekly_active_time_last_6_months",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activeminutes.average_weekly_active_time_last_6_months",
      "test_value": "120",
      "test_value_placeholder": "120",
      "type": "Builtin",
      "unit": "minutes"
    },
    {
      "category": "ActiveMinutes",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/",
          "endpoint": "https://api.fitbit.com /1/user/[user-id]/activities/list.json ",
          "method": ""
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Number",
      "description": "Average weekly minutes spend doing activities",
      "enabled": false,
      "id": 10,
      "index": null,
      "info": "Average weekly minutes spend doing activities over the last 6 months.",
      "is_indexed_variable": false,
      "label": "Average Weekly Activity Time Last 6 Months",
      "name": "average_weekly_activity_time_last_6_months",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activeminutes.average_weekly_activity_time_last_6_months",
      "test_value": "120",
      "test_value_placeholder": "120",
      "type": "Builtin",
      "unit": "minutes"
    },
    {
      "category": "ActiveMinutes",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-interval/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/active-zone-minutes/date/[start-date]/[end-date].json",
          "method": ""
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Number",
      "description": "Average weekly heart zone minutes",
      "enabled": true,
      "id": 11,
      "index": null,
      "info": "Average weekly heart zone minutes over the last 6 months.",
      "is_indexed_variable": false,
      "label": "Average Weekly Heart Zone Minutes Last 6 Months",
      "name": "average_weekly_heart_zone_time_last_6_months",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.activeminutes.average_weekly_heart_zone_time_last_6_months",
      "test_value": "120",
      "test_value_placeholder": "120",
      "type": "Builtin",
      "unit": "minutes"
    },
    {
      "category": "Daily",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/tracker/steps/date/[start-date]/[end-date].json",
          "method": ""
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Date",
      "description": "Date of step count achieved on a single day within the last 6 months. This includes wearable activity tracker data only.",
      "enabled": true,
      "id": 12,
      "index": null,
      "info": "Date of highest daily step count in last 6 months.",
      "is_indexed_variable": false,
      "label": "Date of Highest Daily Step Count in Last 6 Months",
      "name": "highest_steps_last_6_months_date",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.daily.highest_steps_last_6_months_date",
      "test_value": "2020-01-01",
      "test_value_placeholder": "2020-01-01",
      "type": "Builtin",
      "unit": "date"
    },
    {
      "category": "Daily",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/tracker/steps/date/[start-date]/[end-date].json",
          "method": ""
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Number",
      "description": "Highest step count achieved on a single day within the last 6 months. This includes wearable activity tracker data only.",
      "enabled": true,
      "id": 13,
      "index": null,
      "info": "Highest daily step count in last 6 months.",
      "is_indexed_variable": false,
      "label": "Highest Daily Step Count in Last 6 Months",
      "name": "highest_steps_last_6_months_steps",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.daily.highest_steps_last_6_months_steps",
      "test_value": "20000",
      "test_value_placeholder": "20000",
      "type": "Builtin",
      "unit": "steps"
    },
    {
      "category": "Steps",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
          "method": "activities_frequent"
        },
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/create-activity-log/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities.json",
          "method": "lifetime_stats"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Number",
      "description": "Average lifetime steps. If steps on only active days is not available, this will calculate the average step count using the account creation date and total lifetime steps.",
      "enabled": false,
      "id": 14,
      "index": null,
      "info": "Average lifetime steps. ",
      "is_indexed_variable": false,
      "label": "Average Lifetime Steps",
      "name": "average",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.steps.average",
      "test_value": "10000",
      "test_value_placeholder": "10000",
      "type": "Builtin",
      "unit": "steps"
    },
    {
      "category": "Steps",
      "data_origin": [
        {
          "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/create-activity-log/",
          "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities.json",
          "method": "lifetime_stats"
        }
      ],
      "data_provider": "fitbit",
      "data_type": "Number",
      "description": "Highest step count achieved on a single day. This includes wearable activity tracker data only.",
      "enabled": false,
      "id": 15,
      "index": null,
      "info": "Highest step count achieved on a single day. ",
      "is_indexed_variable": false,
      "label": "Highest Lifetime Steps",
      "name": "highest",
      "provider_type": "oauth",
      "qualified_name": "dds.fitbit.builtin.steps.highest",
      "test_value": "20000",
      "test_value_placeholder": "20000",
      "type": "Builtin",
      "unit": "steps"
    }
  ]
}
