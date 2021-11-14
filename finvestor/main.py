from fastapi import FastAPI
from finvestor.db.session import database

app = FastAPI(
    debug=False,
    title="Finvestor",
    description="Finvestor API for managing your etoro/alpaca accounts.",
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
