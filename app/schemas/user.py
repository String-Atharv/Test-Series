from pydantic import BaseModel,EmailStr
from uuid import UUID
from datetime import datetime


class UserCreateRequest(BaseModel):
    username:str
    email:EmailStr
    password:str
    role:str


class UserCreateResponse(BaseModel):
    id:UUID
    username:str
    email:EmailStr
    created_at:datetime

    class Config:
        from_attributes=True #by default pydantic expects dictionary , so when we provide the python objects or orm models,then it cannot unpack the class attributes directly, it will throw an error if we dont provide this config, so from_attributes=true tells that extract data from orm model attributes, not using dictionary

    