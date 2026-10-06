# create jwt token
import jwt
from datetime import datetime,timezone,timedelta
from app.core.config import setting

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


# intialise password hasher
password_hasher=PasswordHash((Argon2Hasher(),))

def create_access_token(user_id: str, role: str):
    # create expiration time
    expire=datetime.now(timezone.utc)+timedelta(minutes=setting.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    # create payload
    payload={
        "sub":user_id,
        "exp":expire,
        "role":role
    }

    # encode and sign the payload using secret key
    token=jwt.encode(payload,setting.JWT_SECRET_KEY,algorithm=setting.JWT_ALGORITHM)

    return token 

def hash_password(password:str) -> str:
    return password_hasher.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return password_hasher.verify(plain_password,hashed_password)





