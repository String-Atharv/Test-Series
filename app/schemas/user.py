from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime


class UserCreateRequest(BaseModel):
    username:str
    email:EmailStr
    password:str
    role:str

class UserLoginRequest(BaseModel):
    email:EmailStr
    password:str


class UserCreateResponse(BaseModel):
    id:UUID
    username:str
    email:EmailStr
    created_at:datetime

    model_config = ConfigDict(from_attributes=True) # by default pydantic expects dictionary , so when we provide the python objects or orm models,then it cannot unpack the class attributes directly, it will throw an error if we dont provide this config, so from_attributes=true tells that extract data from orm model attributes, not using dictionary

    