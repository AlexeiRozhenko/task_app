from fastapi import FastAPI
from app.routes.tasks import router_tasks
from app.routes.auth import router_auth
from app.database import engine, Base
# uvicorn app.main:app --reload

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(
    router_tasks,
    prefix="/api/tasks",
    tags=["Tasks"]
)

app.include_router(
    router_auth,
    prefix="/api/auth",
    tags=["Authorization"]
)

@app.get("/api")
def read_root():
    return {"Hello": "World"}