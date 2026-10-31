import json

from sqlmodel import SQLModel, Field

class TripInput(SQLModel):
    start: int
    end: int
    description: str

class TripOutput(TripInput):
    id: int

class CarInput(SQLModel):
    size: str
    fuel: str | None = "electric"
    doors: int
    transmission: str | None = "auto"

class Car(CarInput, table=True):
    id: int | None = Field(primary_key=True, default=None)

class CarOutput(CarInput):
    id: int
    trips: list[TripOutput] = []

def load_db() -> list[CarOutput]:
    with open("cars.json") as f:
        return [CarOutput.model_validate(obj) for obj in json.load(f)]

def save_db(cars: list[CarOutput]):
    with open("cars.json", "w") as f:
        json.dump([car.model_dump() for car in cars], f, indent=4)