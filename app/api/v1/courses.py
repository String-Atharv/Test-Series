from starlette.status import HTTP_204_NO_CONTENT,HTTP_201_CREATED,HTTP_200_OK
from uuid import UUID 
from app.services.course_service import CourseService
from fastapi import Depends,APIRouter
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession 
from app.schemas.course import CourseCreateRequest,CourseResponse,CourseUpdateRequest

router=APIRouter(prefix="/courses",tags=["courses"])

# create course
@router.post("/",response_model=CourseResponse,status_code=HTTP_201_CREATED)
async def create_course(request:CourseCreateRequest,db:AsyncSession=Depends(get_db)):
   course = await CourseService.create_course(db,request)
   await db.commit()
   return course

#get course by id
@router.get("/{id}",response_model=CourseResponse,status_code=HTTP_200_OK)
async def get_course_by_id(id:UUID,db:AsyncSession=Depends(get_db)):
    course=await CourseService.get_course_by_id(db,id)
    await db.commit()
    return course

# get all the courses
@router.get("/",response_model=list[CourseResponse],status_code=HTTP_200_OK)
async def get_all_courses(db:AsyncSession=Depends(get_db)):
    courses=await CourseService.get_all_courses(db)
    await db.commit()
    return courses

# delete the course
@router.delete("/{id}",status_code=HTTP_204_NO_CONTENT)
async def delete_course(id:UUID,db:AsyncSession=Depends(get_db)):
    await CourseService.delete_course(db,id)
    await db.commit()
    
# update the complete course
@router.put("/{id}",response_model=CourseResponse,status_code=HTTP_200_OK)
async def update_course(id:UUID,request:CourseUpdateRequest,db:AsyncSession=Depends(get_db)):
    updated_course=await CourseService.update_course(db,id,request)
    await db.commit()
    return updated_course







