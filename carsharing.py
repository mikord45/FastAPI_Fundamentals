from fastapi import FastAPI, HTTPException

from schemas import load_db, CarInput, save_db, CarOutput

app = FastAPI()

db = load_db()

@app.get("/api/cars")
async def get_cars(size: str|None = None, doors: int|None = None) -> list[CarOutput]:
    result = db
    if size:
        result = [car for car in result if car.size == size]
    if doors:
        result = [car for car in result if car.doors >= doors]
    return result

@app.get("/api/cars/{id}")
async def car_by_id(id: int) -> CarOutput:
    result = [car for car in db if car.id == id]
    if result:
        return result[0]
    else:
        raise HTTPException(status_code=404, detail=f"No car with id {id}")

@app.post("/api/cars")
def add_car(car: CarInput) -> CarOutput:
    new_car = CarOutput(id=len(db) + 1, **car.model_dump())
    db.append(new_car)
    save_db(db)
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

@app.get("/")
async def welcome(name):
    return {"message": f"Welcome, {name} to the Car Sharing service!"}

# if __name__ == "__main__":
#     uvicorn.run("carsharing:app", reload=True)
