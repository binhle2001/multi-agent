from pydantic import BaseModel

class Query_HRM(BaseModel):
    content: str
    class Config:
        json_schema_extra = {
            "content": "str",
        }

class QueryMachine(BaseModel):
    content: str
    class Config:
        json_schema_extra = {
            "content": "str",
        }

class QueryMaterial(BaseModel):
    content: str
    class Config:
        json_schema_extra = {
            "content": "str",
        }

class Chat(BaseModel):
    content: str
    class Config:
        json_schema_extra = {
            "content": "str",
        }
    

class Plan(BaseModel):
    date: str
    class Config:
        json_schema_extra = {
            "date": "str",
        }


