from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from schemas import load_db, CarInput, save_db, CarOutput, TripOutput, TripInput, Car
from sqlmodel import create_engine, SQLModel, Session, select

engine = create_engine("sqlite:///carsharing.db", connect_args={"check_same_thread": False}, echo=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Car Sharing Service", lifespan=lifespan)

db = load_db()

@app.get("/api/cars")
async def get_cars(size: str|None = None, doors: int|None = None) -> list[Car]:
    with Session(engine) as session:
        query = select(Car)
        if size:
            query = query.where(Car.size == size)
        if doors:
            query = query.where(Car.doors >= doors)
        return list(session.exec(query).all())

@app.get("/api/cars/{id}")
async def car_by_id(id: int) -> CarOutput:
    result = [car for car in db if car.id == id]
    if result:
        return result[0]
    else:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")

@app.post("/api/cars")
def add_car(car_input: CarInput) -> Car:
    with Session(engine) as session:
        new_car = Car.model_validate(car_input)
        session.add(new_car)
        session.commit()
        session.refresh(new_car)
        return new_car

@app.delete("/api/cars/{id}", status_code=204)
def remove_car(id: int) -> None:
    matches = [car for car in db if car.id == id]
    if matches:
        car = matches[0]
        db.remove(car)
        save_db(db)
    else:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")

@app.put("/api/cars/{id}")
def change_car(id: int, new_data: CarInput) -> CarOutput:
    car = next((car for car in db if car.id == id), None)
    if car is None:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")
    for field, value in new_data.model_dump().items():
        setattr(car, field, value)
    save_db(db)
    return car

@app.post("/api/cars/{car_id}/trips")
def add_trip(car_id: int, trip: TripInput) -> TripOutput:
    car = next((car for car in db if car.id == car_id), None)
    if car is None:
        raise HTTPException(status_code=404, detail=f"No car with id {car_id}")
    new_trip = TripOutput(id=len(car.trips) + 1, **trip.model_dump())
    car.trips.append(new_trip)
    save_db(db)
    return new_trip

@app.get("/")
async def welcome(name):
    return {"message": f"Welcome, {name} to the Car Sharing service!"}

# if __name__ == "__main__":
#     uvicorn.run("carsharing:app", reload=True)
