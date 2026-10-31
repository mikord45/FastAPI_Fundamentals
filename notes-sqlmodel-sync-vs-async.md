# SQLModel: sync vs async sessions

## Why the course uses no `async`/`await` with SQLModel

SQLModel's `Session` and `create_engine` are **synchronous**. With `sqlite:///...` the driver is
Python's built-in `sqlite3`, which blocks the calling thread on every query. A blocking call
can't be awaited, so adding `await` in front of `session.exec(...)` doesn't work.

This is a property of the sync driver and session, not a limit of SQLModel itself.

## How FastAPI handles sync DB code

- A plain `def` endpoint runs in a **threadpool**. A blocking DB call blocks only that thread.
- An `async def` endpoint runs **on the event loop**. A blocking call inside it freezes all other
  requests until it finishes.

So with the sync `Session`, endpoints should be plain `def`.

> An `async def` endpoint that uses the sync session blocks the event loop while a query runs.

## Async SQLModel does exist

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

engine = create_async_engine("sqlite+aiosqlite:///carsharing.db")

async def get_session():
    async with AsyncSession(engine) as session:
        yield session

@app.get("/api/cars")
async def get_cars(session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.exec(select(Car))
    return result.all()
```

Things to know:

- Needs an **async driver**: `aiosqlite` for SQLite, `asyncpg` for PostgreSQL. Swapping only the
  session class is not enough.
- Not every session call is awaited. `add()` stays plain; `exec`, `commit`, `refresh`, `get`
  and `delete` need checking against the installed version's docs.
- **Lazy loading breaks.** Reading `car.trips` triggers a hidden query, which raises
  `MissingGreenlet` in async code. Use eager loading (`selectinload`) wherever relationships
  are read, e.g. `CarOutput` with its trips.

## Why the course and the SQLModel docs stay sync (likely reasons, not confirmed)

1. Sync is simpler to teach; async adds a driver, an async engine, `AsyncSession`, `await`
   everywhere and the lazy-loading problem.
2. Sync is enough for most apps, since FastAPI runs `def` endpoints in a threadpool.
3. SQLModel's tutorial teaches concepts with the simplest session, and its async support is a
   thin layer over SQLAlchemy's with little dedicated documentation.

The actual reasoning of the course author is unknown.

## Takeaway for this project

Keep the sync `Session`, and make endpoints that use it plain `def`.
