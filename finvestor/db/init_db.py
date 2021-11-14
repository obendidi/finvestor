from sqlalchemy.orm import Session

from finvestor.db import base  # noqa: F401

# make sure all SQL Alchemy models are imported (finvestor.db.base) before initializing
# DB otherwise, SQL Alchemy might fail to initialize relationships properly


def init_db(db: Session) -> None:
    pass
