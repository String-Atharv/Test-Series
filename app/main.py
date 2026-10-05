from fastapi import FastAPI
from app.core.config import setting
from app.api.v1.users import router as user_router

# create the fastapi app
app=FastAPI(
    title=setting.PROJECT_NAME
)

#include the users router
app.include_router(user_router,prefix="/api/v1",tags=["users"])


#simple health check endpoint 
@app.get("/")
async def health_check():
    return{"status":"ok"}

