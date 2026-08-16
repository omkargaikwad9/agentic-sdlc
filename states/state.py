from typing import TypedDict,List,Optional


class AgentState(TypedDict):
    user_request:dict

    metadata:list

    impacted_analysis:dict

    file_content:dict

    generated_code:dict

    validation_result:dict

    messages:list
