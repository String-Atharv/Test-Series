from app.schemas.user import UserCreateResponse,UserCreateRequest
from fastapi import APIRouter , Depends , status
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService

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