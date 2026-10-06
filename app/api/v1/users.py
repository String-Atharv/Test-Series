from starlette.status import HTTP_200_OK
from app.schemas.user import UserCreateResponse,UserCreateRequest,UserLoginRequest
from app.schemas.token import Token
from fastapi import APIRouter , Depends , status, HTTPException
from app.core.security import create_access_token
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService
from app.api.deps import get_current_user_from_jwt
from app.models.common.User import User

router = APIRouter(prefix="/users",tags=["users"])

@router.post("/register",response_model=UserCreateResponse,status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data:UserCreateRequest,
    db:AsyncSession=Depends(get_db) # thisautomatically gives the DB session , as and when router function is called , it will call the get_db() function and return the DB session 
):
    new_user=await UserService.register_user(db,user_data)
    await db.commit()

    # return the created user in the response 
    return new_user # here response_model=UserCreateResponse intercepts the returned object and converts the orm model to pydantic model using the Config.from_attributes=true config


@router.post("/authenticate",response_model=Token,status_code=HTTP_200_OK)
async def authenticate(login:UserLoginRequest,db:AsyncSession=Depends(get_db)):
    # 1. Authenticate user (HTTP Exceptions are already handled in the Service!)
    user=await UserService.authenticate_user(db,login)

    # 2. Generate the JWT token (convert UUID to string)
    access_token = create_access_token(user_id=str(user.id), role=user.role.name)

    # 3. Return the token in the exact format Pydantic expects
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserCreateResponse)
async def get_my_profile(current_user: User = Depends(get_current_user_from_jwt)):
    """
    Fetch the currently authenticated user's details.
    """
    return current_user
