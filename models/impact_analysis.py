from pydantic import BaseModel
from typing import List ,Optional,Literal


class ImpactAnalysis(BaseModel):
    file_to_edit:List[str]
    function_to_edit:List[str]
    affected_files:List[str]
    reason:str
