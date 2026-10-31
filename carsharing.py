from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends
from schemas import CarInput, CarOutput, TripOutput, TripInput, Car, Trip
from sqlmodel import create_engine, SQLModel, Session, select

engine = create_engine("sqlite:///carsharing.db", connect_args={"check_same_thread": False}, echo=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="Car Sharing Service", lifespan=lifespan)

@app.get("/api/cars")
def get_cars(session: Annotated[Session, Depends(get_session)], size: str|None = None, doors: int|None = None) -> list[CarOutput]:
    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors >= doors)
    return list(session.exec(query).all())

@app.get("/api/cars/{id}")
def car_by_id(session: Annotated[Session, Depends(get_session)], id: int) -> CarOutput:
    car = session.get(Car, id)
    if car:
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")

@app.post("/api/cars")
def add_car(session: Annotated[Session, Depends(get_session)], car_input: CarInput) -> Car:
    new_car = Car.model_validate(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)
    return new_car

@app.delete("/api/cars/{id}", status_code=204)
def remove_car(session: Annotated[Session, Depends(get_session)], id: int) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")

@app.put("/api/cars/{id}")
def change_car(session: Annotated[Session, Depends(get_session)], id: int, new_data: CarInput) -> Car:
    car = session.get(Car, id)
    if car is None:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")
    for field, value in new_data.model_dump().items():
        setattr(car, field, value)
    session.commit()
    return car

@app.post("/api/cars/{car_id}/trips")
def add_trip(session: Annotated[Session, Depends(get_session)], car_id: int, trip_input: TripInput) -> Trip:
    car = session.get(Car, car_id)
    if car is None:
        raise HTTPException(status_code=404, detail=f"No car with id {car_id}")
    new_trip = Trip.model_validate(trip_input, update={'car_id': car_id})
    car.trips.append(new_trip)
    session.commit()
    session.refresh(new_trip)
    return new_trip

@app.get("/")
async def welcome(name):
    return {"message": f"Welcome, {name} to the Car Sharing service!"}

# if __name__ == "__main__":
#     uvicorn.run("carsharing:app", reload=True)
