# Data Providers

```mermaid
classDiagram
direction TB
class DataProvider {
    instructions
    name
    name_lower
    label
    value
    registry
    name
    name_lower
    label
    value
    instructions
   register(cls) 
   register_subclasses(cls, class_=None) 
   get_class_by_name(cls, name) 
   get_class_by_value(cls, value) 
}
class DataProviderUI {
    _redirect_uri
    registry
    DataProviderUI.DataCategory
   register(cls) 
   get_form_fields() 
   get_all_variables() 
   fields(cls) 
   variables(cls) 
   get_client_id(self) 
   redirect_uri(self) 
   get_redirect_uri(cls) 
   get_authorize_url(self) 
   connect(self) 
   request_token(self, code: str) 
   get_data_categories(cls) 
   get_all_data_categories() 
}
class DataProviderUser {
    _all_initial_funcs
    _factory_funcs
    _variable_values
    _variable_funcs
    registry
    _all_initial_funcs
    _factory_funcs
    _variable_funcs
   __init__(self) 
   register(cls) 
   all_initial_funcs(self) 
   factory_funcs(self) 
   variable_funcs(self) 
   calculate_variables(self, project_variables) 
   __getitem__(self, name) 
}
class FitbitDataProviderUI {
    fitbit
    _client_id
    _client_secret
    _redirect_uri
    instructions
    _token_url
    _revoke_url
    _scopes
    FitbitDataProviderUI.DataCategory
    FitbitDataProviderUI.client_id
    FitbitDataProviderUI.client_secret
    FitbitDataProviderUI.account_creation_date
    FitbitDataProviderUI.most_frequent_activity
    FitbitDataProviderUI.second_most_frequent_activity
    FitbitDataProviderUI.average_lifetime_steps
    FitbitDataProviderUI.best_lifetime_steps
    FitbitDataProviderUI.UserFitBit
   __init__(self, client_id: str = None, client_secret: str = None, redirect_uri: str = None, **kwargs) 
   get_client_id(self) 
   get_authorize_url(self, scope: list[str] = None) 
   token_url(self) 
   revoke_url(self) 
   scopes(self) 
   redirect_uri(self) 
   connect(self) 
   revoke_token(self, token: str) 
   request_token(self, code: str) 
}
class FitbitDataProviderUser {
    access_token
    fitbit
    refresh_token
    client_secret
    client_id
   __init__(self, client_id: str = None, client_secret: str = None,
                 access_token: str = None, refresh_token: str = None, **kwargs) 
   connect(self) 
   user_profile(self) 
   activities_favorite(self) 
   activities_frequent(self) 
   activities_recent(self) 
   lifetime_stats(self) 
   fetch_account_creation_date(self) 
   fetch_most_frequent_activity(self) 
   fetch_second_most_frequent_activity(self) 
   fetch_average_daily_steps(self) 
   factory_activities_by_frequency(self, idx=0) 
}

DataProvider  -->  DataProviderUser 
DataProvider  -->  DataProviderUI 
DataProviderUser  -->  FitbitDataProviderUser
DataProviderUI  -->  FitbitDataProviderUI

```
