from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session
from schemas import CarOutput, Car, CarInput, TripInput, Trip

router = APIRouter(prefix="/api/cars")

@router.get("/")
def get_cars(session: Annotated[Session, Depends(get_session)], size: str | None = None, doors: int | None = None) -> list[CarOutput]:
    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors >= doors)
    return list(session.exec(query).all())


@router.get("/{id}")
def car_by_id(session: Annotated[Session, Depends(get_session)], id: int) -> CarOutput:
    car = session.get(Car, id)
    if car:
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")


@router.post("/")
def add_car(session: Annotated[Session, Depends(get_session)], car_input: CarInput) -> Car:
    new_car = Car.model_validate(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)
    return new_car


@router.delete("/{id}", status_code=204)
def remove_car(session: Annotated[Session, Depends(get_session)], id: int) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")


@router.put("/{id}")
def change_car(session: Annotated[Session, Depends(get_session)], id: int, new_data: CarInput) -> Car:
    car = session.get(Car, id)
    if car is None:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")
    for field, value in new_data.model_dump().items():
        setattr(car, field, value)
    session.commit()
    return car


@router.post("/{car_id}/trips")
def add_trip(session: Annotated[Session, Depends(get_session)], car_id: int, trip_input: TripInput) -> Trip:
    car = session.get(Car, car_id)
    if car is None:
        raise HTTPException(status_code=404, detail=f"No car with id {car_id}")
    new_trip = Trip.model_validate(trip_input, update={'car_id': car_id})
    car.trips.append(new_trip)
    session.commit()
    session.refresh(new_trip)
    return new_trip
