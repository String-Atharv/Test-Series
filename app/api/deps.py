# dependency to take access token from every request , extract user from it and allow user to access the api-endpoint if user is authorized

from app.core.config import setting
import jwt
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.models import User
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi import Depends
from app.database.session import get_db
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/users/authenticate")
#token_url : this api-endpoint is called to get the jwt token 
#OAuth2PasswordBearer:that extracts a Bearer token from the request's Authorization header.
async def get_current_user_from_jwt(token:str=Depends(oauth2_scheme),db:AsyncSession=Depends(get_db))-> User:

    credentials_exception=HTTPException(status_code=HTTP_401_UNAUTHORIZED,detail="could not authenticate credentials",headers={"WWW-Authenticate":"Bearer"})
    try:
        #decode the jwt token to payload
        payload=jwt.decode(token,setting.JWT_SECRET_KEY,algorithms=[setting.JWT_ALGORITHM])

        #extract the user_id from paylod
        id=payload.get("sub")
        if id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    #fetch the user from db
    user=await UserRepository.get_user_by_id(db,id)
    if user is None:
        raise credentials_exception
    return user




    

