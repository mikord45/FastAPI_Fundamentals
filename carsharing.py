from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from db import engine
from sqlmodel import SQLModel
from routers import cars, web, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Car Sharing Service", lifespan=lifespan)
app.include_router(cars.router)
app.include_router(web.router)
app.include_router(auth.router)

origins = [
    "http://localhost:8080",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(cars.BadTripException)
async def bad_trip_exception_handler(request: Request, exc: cars.BadTripException):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"message": "Bad Trip"})

@app.middleware("http")
async def add_cars_cookie(request: Request, call_next):
    response = await call_next(request)
    response.set_cookie(key="cars_cookie", value="you_visited_the_carsharing_app")
    return response

# @app.get("/")
# async def welcome(name):
#     return {"message": f"Welcome, {name} to the Car Sharing service!"}

# if __name__ == "__main__":
#     uvicorn.run("carsharing:app", reload=True)
