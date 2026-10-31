import json

from sqlmodel import SQLModel, Field, Relationship

class TripInput(SQLModel):
    start: int
    end: int
    description: str

class Trip(TripInput, table=True):
    id: int | None = Field(default=None, primary_key=True)
    car_id: int = Field(foreign_key="car.id")
    car: "Car" = Relationship(back_populates="trips")

class TripOutput(TripInput):
    id: int

class CarInput(SQLModel):
    size: str
    fuel: str | None = "electric"
    doors: int
    transmission: str | None = "auto"

class Car(CarInput, table=True):
    id: int | None = Field(primary_key=True, default=None)
    trips: list[Trip] = Relationship(back_populates="car", cascade_delete=True)

class CarOutput(CarInput):
    id: int
    trips: list[TripOutput] = []
