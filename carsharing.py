from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import engine
from sqlmodel import SQLModel
from routers import cars, web

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Car Sharing Service", lifespan=lifespan)
app.include_router(cars.router)
app.include_router(web.router)

@app.get("/")
async def welcome(name):
    return {"message": f"Welcome, {name} to the Car Sharing service!"}

# if __name__ == "__main__":
#     uvicorn.run("carsharing:app", reload=True)
