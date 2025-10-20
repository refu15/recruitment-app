from pydantic import BaseModel
from typing import Optional

class StageBase(BaseModel):
    stage_name: str
    criteria_filename: str
    order: int

class StageCreate(StageBase):
    pass

class Stage(StageBase):
    id: str

    class Config:
        orm_mode = True
