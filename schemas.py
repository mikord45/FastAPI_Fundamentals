import json
from pydantic import BaseModel

class Car(BaseModel):
    id: int
    size: str
    fuel: str | None = "electric"
    doors: int
    transmission: str | None = "auto"

def load_db() -> list[Car]:
    with open("cars.json") as f:
        return [Car.model_validate(obj) for obj in json.load(f)]