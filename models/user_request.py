from pydantic import BaseModel
from typing import List, Optional, Union


class user_request(BaseModel):
    action:List[str]
    description:str