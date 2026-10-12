# from app.schemas.course import CourseCreateRequest
# from uuid import UUID
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from app.models.course_hierarchy.CaCourses import CaCourses
# from app.models.common.enums import CACourses


# class CourseRepository:

#     @staticmethod
#     async def create_course(db: AsyncSession, course_data: CourseCreateRequest) -> CaCourses:
#         course = CaCourses(**course_data)
#         db.add(course)
#         await db.flush()
#         await db.refresh(course)
#         return course

#     @staticmethod
#     async def get_course_by_id(db: AsyncSession, course_id: UUID) -> CaCourses | None:
#         stmt = select(CaCourses).where(CaCourses.id == course_id)
#         result = await db.execute(stmt)
#         return result.scalar_one_or_none()

#     @staticmethod
#     async def get_course_by_name(db: AsyncSession, name: CACourses) -> CaCourses | None:
#         stmt = select(CaCourses).where(CaCourses.name == name)
#         result = await db.execute(stmt)
#         return result.scalar_one_or_none()

#     @staticmethod
#     async def get_course_by_display_order(db: AsyncSession, display_order: int) -> CaCourses | None:
#         stmt = select(CaCourses).where(CaCourses.display_order == display_order)
#         result = await db.execute(stmt)
#         return result.scalar_one_or_none()

#     @staticmethod
#     async def get_all_courses(db: AsyncSession) -> list[CaCourses]:
#         stmt = select(CaCourses).order_by(CaCourses.display_order)
#         result = await db.execute(stmt)
#         return list(result.scalars().all())

#     @staticmethod
#     async def update_course(db: AsyncSession, course: CaCourses, update_data: dict) -> CaCourses:
#         for field, value in update_data.items():
#             if value is not None:
#                 setattr(course, field, value)
#         await db.flush()
#         await db.refresh(course)
#         return course

#     @staticmethod
#     async def delete_course(db: AsyncSession, course: CaCourses) -> None:
#         await db.delete(course)
#         await db.flush()


from app.schemas.course import CourseUpdateRequest
import string
from sqlalchemy import select, delete
from uuid import UUID
from app.models.course_hierarchy.CaCourses import CaCourses
from app.models.common.enums import CACourses
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.course import CourseCreateRequest
class CourseRepository:
    
    @staticmethod
    async def create_course(db:AsyncSession,course_data:CourseCreateRequest):
        # now session cannot act on the pydantic model , we need to convert it into python dict , then to orm model

        dict=course_data.model_dump() # converts to python dict
        course=CaCourses(**dict) # convert to orm model , **dict -> unpacks the key-value pair and converts it into keyword arguments
        #for ex dict={"name":"atharv","age":"12"} , **dict -> name=atharv,age=12 this is keyword arguments , which is then passed in to function / objects 
        # here in this case we are creating the CaCourses obj , so we need to pass the name and displayorder values as keyword arugments , so we done like this CaCourses(name=dict["name"],age=dict["age"])

        db.add(course)
        await db.flush() # this sends sql to db to execute 
        await db.refresh(course) # after executing sql , we get id and refresh updated all the fields (including id ) so now our course has id
        return course

    @staticmethod
    async def get_course_by_id(db:AsyncSession,course_id:UUID) ->CaCourses|None:
        stmt = select(CaCourses).where(CaCourses.id == course_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_course_by_name(db:AsyncSession,name:CACourses) -> CaCourses | None:
        stmt = select(CaCourses).where(CaCourses.name==name)
        result=await db.execute(stmt) # result is Result obj
        course=result.scalar_one_or_none() # course is CaCourses model object
        return course

    @staticmethod
    async def get_course_by_display_order(db:AsyncSession,display_order:int) -> CaCourses | None:
        stmt = select(CaCourses).where(CaCourses.display_order==display_order)
        result=await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_courses(db:AsyncSession):
        stmt=select(CaCourses).order_by(CaCourses.display_order)
        result=await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_course_by_id(db:AsyncSession,id:UUID):
        stmt=delete(CaCourses).where(CaCourses.id==id)
        await db.execute(stmt)
        await db.flush()

    @staticmethod
    async def update_course(db:AsyncSession,id:UUID,request:CourseUpdateRequest):

        #fetch the existing record
        course=await CourseRepository.get_course_by_id(db,id)
        if not course:
            return None
        
        course_dict=request.model_dump(exclude_unset=True) # excludes the unset values , for ex ("name:None","display_order":2) here name is unset so we need to exclude the name

        # Apply the updates to ORM object
        for field,values in course_dict.items():
            setattr(course,field,values)

        #now the course obj is updated , now just flush and refresh to see the changes

        await db.flush()
        await db.refresh(course)
        return course

        

        
        


    


    




    

    

