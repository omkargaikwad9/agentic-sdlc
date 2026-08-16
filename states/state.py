from typing import TypedDict,List,Optional,Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage



class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], 
                        add_messages,
                        ]
    repository_path: str
    issue_number: int
    issue_title: str
    issue_body: str
