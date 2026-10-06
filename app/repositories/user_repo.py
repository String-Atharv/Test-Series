from sqlalchemy.ext.asyncio import AsyncSession
from app.models.common.User import User
from sqlalchemy import select

class UserRepository:

    @staticmethod
    async def get_user_by_id(db:AsyncSession,id:str)->User|None:
        stmt=select(User).where(User.id==id)
        result=await db.execute(stmt)
        return result.scalar_one_or_none()


    @staticmethod
    async def get_user_by_email(db:AsyncSession,email:str)->User | None:
        # Build the sql query using sqlalchemy syntax
        stmt=select(User).where(User.email==email)

        #Execute the sql query
        result=await db.execute(stmt)

        #Extract the first row , return none if not found
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db:AsyncSession,user_data:dict) -> User:
        # saves new user to db
        #convert the user dict to user model instance

        user = User(**user_data) # unpacks the user_data and pass it to the User model constructor

        # add user to session
        db.add(user)

        # flush sends the sql stmt to db to execute without commiting the transaction , it is done to get ID , because id is generated after the sql stmt is executed

        await db.flush()

        # refresh update the user object with latest changes from db like id 

        await db.refresh(user)
        
        return user

        

    

