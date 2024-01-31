# Administrator Flow

```mermaid
---
title: Administrator Flow
---
flowchart TD
    R{{fa:fa-glasses Researcher}} --> | Connect to | admin_page(Admin page)
    admin_page --> | fa:fa-mouse-pointer Select | project(Project) --> |Select| available_data_providers
    admin_page --> | Specify | admin_page_specify
    
    available_data_providers --> | fa:fa-mouse Click | manage_variables_button(Manage variables button)
    
    manage_variables_button --> variables_management
    
    variables_management --> | fa:fa-mouse Click | sync_button(Synchronize variables button v1) 
    sync_button --> | Start | variables_sync
    variables_management --> | Automatic generation | survey_url(Survey URL v2)
    

    
    subgraph admin_page_specify [Required Qualtrics Information v0]
        direction LR
        Qualtrics_API_Key(Qualtrics API Key)
        Qualtrics_Survey_ID(Qualtrics Survey ID)
    end
    
    subgraph available_data_providers [Data Providers]
        fitbit(Fitbit v0) & facebook(<s>Facebook</s> v10) --> enter_provider_api_key[Enter API keys. v1]
    end
    
    subgraph manage_variables_button [Manage Variables Button v2]
         current_variables[Fetch variables used in survey] --> update_selected_variables[Update selected variables]
    end
    
    subgraph variable_selection_ui [Variable selection UI v1]
            initial_variables(Initial variables:\n- creation date\n- total steps)
    end
    
    subgraph custom_variables_ui [Custom variables UI v2]
            custom_variables_functionality(Expose JS, SQL, or Python?)
    end
    
    subgraph variables_management [Variables Management v1]
        direction LR
        custom_variables_ui <--> variable_selection_ui
    end
    
    subgraph variables_sync [fa:fa-sync Variable Sync]
        fetch_variables_from_qualtrics[fa:fa-download Fetch variables from survey v3] --> | Update variables list | latest_variables_list[Latest variables list v3]
        latest_variables_list --> | Upload to | variables_sync_qualtrics[Qualtrics v0]
    end

```

%%---
%%title: Title example
%%---
%%flowchart LR
%%    A --> B
%%    subgraph name
%%    C --> D
%%    end
%%    id1([This is the text in the box])
%%    id2["This is the (text) in the box"]

%%stateDiagram-v2
%%    S1: The state with a note
%%    note right of S1
%%    This is note
%%    end note

%%classDiagram
%%class Square~Shape~{
%%    int id
%%    List~int~ position
%%    setPoints(List~int~ points)
%%    getPoints() List~int~
%%}
%%
%%Square : -List~string~ messages
%%Square : +setMessages(List~string~ messages)
%%Square : +getMessages() List~string~
%%Square : +getDistanceMatrix() List~List~int~~

%% This is comment

