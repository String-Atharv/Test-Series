from alembic.util import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreateRequest,UserCreateResponse,UserLoginRequest
from app.repositories.user_repo import UserRepository
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from fastapi import HTTPException
from app.schemas.token import Token
from app.models.common.User import User
from app.core.security import verify_password



#Intialise the password hasher using the Argon2 algorithm
password_hasher=PasswordHash((Argon2Hasher(),))


class UserService:
    @staticmethod
    async def register_user(db:AsyncSession,user:UserCreateRequest):
        # first check if the user already exists using UserRepository
        existing_user=await UserRepository.get_user_by_email(
            db,
            user.email)
        if existing_user:
            # raise a 400 bad request 
            raise HTTPException(
                status_code=400,
                detail="user already exists"
                )
        # hash the plain text password from the request
        hashed_password=password_hasher.hash(user.password)

        # create user model to save in db

        user_dict={
            "username":user.username,
            "email":user.email,
            "password":hashed_password,
            "role":user.role
        }

        #call the Repository to save the user to db
        created_user=await UserRepository.create_user(db,user_dict)

        # return the created database model to router
        return created_user

    @staticmethod
    async def authenticate_user(db:AsyncSession,request:UserLoginRequest) :
        #fetch the user
        user = await UserRepository.get_user_by_email(db,request.email)
        
        if not user :
            raise HTTPException(
                status_code=404,
                detail="user not registered"
            )

        if not verify_password(request.password,user.password):
            raise HTTPException(status_code=401,detail="invalid credentials")

        return user


        