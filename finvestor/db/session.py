import databases
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from finvestor.core.config import config

database = databases.Database(config.FINVESTOR_DATABASE_URI)
engine = create_engine(config.FINVESTOR_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
