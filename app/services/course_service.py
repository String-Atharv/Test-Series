# from uuid import UUID
# from fastapi import HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.repositories.course_repo import CourseRepository
# from app.schemas.course import CourseCreateRequest, CourseUpdateRequest
# from app.models.course_hierarchy.CaCourses import CaCourses


# class CourseService:

#     @staticmethod
#     async def create_course(db: AsyncSession, request: CourseCreateRequest) -> CaCourses:
#         # Check duplicate name
#         existing_name = await CourseRepository.get_course_by_name(db, request.name)
#         if existing_name:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Course '{request.name.value}' already exists"
#             )

#         # Check duplicate display_order
#         existing_order = await CourseRepository.get_course_by_display_order(db, request.display_order)
#         if existing_order:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Display order {request.display_order} is already taken by course '{existing_order.name.value}'"
#             )

#         course_data = {
#             "name": request.name,
#             "display_order": request.display_order,
#         }
#         return await CourseRepository.create_course(db, course_data)

#     @staticmethod
#     async def get_course_by_id(db: AsyncSession, course_id: UUID) -> CaCourses:
#         course = await CourseRepository.get_course_by_id(db, course_id)
#         if not course:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Course not found"
#             )
#         return course

#     @staticmethod
#     async def get_all_courses(db: AsyncSession) -> list[CaCourses]:
#         return await CourseRepository.get_all_courses(db)

#     @staticmethod
#     async def update_course(db: AsyncSession, course_id: UUID, request: CourseUpdateRequest) -> CaCourses:
#         course = await CourseService.get_course_by_id(db, course_id)

#         update_data = request.model_dump(exclude_unset=True)

#         if "name" in update_data and update_data["name"] != course.name:
#             existing_name = await CourseRepository.get_course_by_name(db, update_data["name"])
#             if existing_name and existing_name.id != course.id:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Course '{update_data['name'].value}' already exists"
#                 )

#         if "display_order" in update_data and update_data["display_order"] != course.display_order:
#             existing_order = await CourseRepository.get_course_by_display_order(db, update_data["display_order"])
#             if existing_order and existing_order.id != course.id:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Display order {update_data['display_order']} is already taken by course '{existing_order.name.value}'"
#                 )

#         return await CourseRepository.update_course(db, course, update_data)

#     @staticmethod
#     async def delete_course(db: AsyncSession, course_id: UUID) -> None:
#         course = await CourseService.get_course_by_id(db, course_id)
#         await CourseRepository.delete_course(db, course)

    
from app.schemas.course import CourseUpdateRequest
from app.models import CaCourses
from starlette.status import HTTP_404_NOT_FOUND
from uuid import UUID
from starlette.status import HTTP_400_BAD_REQUEST
from fastapi import HTTPException
from app.schemas.course import CourseCreateRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.course_repo import CourseRepository
class CourseService:

    @staticmethod
    async def create_course(db:AsyncSession,request:CourseCreateRequest):
        #check if course exists by coursename or display order
        name=await CourseRepository.get_course_by_name(db,request.name)
        if name:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,detail=f"Course already exists by name '{request.name}' ")
        displayorder=await CourseRepository.get_course_by_display_order(db,request.display_order)
        if displayorder:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Display order {request.display_order} is already taken by course '{displayorder.name.value}'"
            )

        return await CourseRepository.create_course(db,request)
        
    @staticmethod
    async def get_course_by_id(db:AsyncSession,id:UUID)->CaCourses:
        # check if the course with this id is present 
        course = await CourseRepository.get_course_by_id(db,id)
        if course is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,detail="Course not found")
        return course

    @staticmethod
    async def get_all_courses(db:AsyncSession) -> list[CaCourses]:
        courses: list[CaCourses] = await CourseRepository.get_all_courses(db)
        return courses

    @staticmethod
    async def delete_course(db:AsyncSession,id:UUID):
        #check if the course is present or not
        course=await CourseRepository.get_course_by_id(db,id)
        if not course:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,detail="Course not found")
        return await CourseRepository.delete_course_by_id(db,id)

    @staticmethod
    async def update_course(db:AsyncSession,id:UUID,request:CourseUpdateRequest):
        # check if the course exists or not
        course=await CourseRepository.get_course_by_id(db,id)
        if not course:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Course not found"
            )
        return await CourseRepository.update_course(db,id,request)

    


    