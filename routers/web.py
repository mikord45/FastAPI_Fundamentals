from typing import Annotated

from fastapi import APIRouter, Request, Form, Depends, Cookie
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from sqlmodel import Session

from db import get_session
from routers.cars import get_cars

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request, cars_cookie: Annotated[str | None, Cookie()] = None):
    print(cars_cookie)
    return templates.TemplateResponse(request, "home.html")

@router.post("/search", response_class=HTMLResponse)
def search(size: Annotated[str, Form()], doors: Annotated[int, Form()], request: Request, session: Annotated[Session, Depends(get_session)]):
    cars = get_cars(size=size, doors=doors, session=session)
    return templates.TemplateResponse(request, "search_results.html", {"cars": cars})
