from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import databases

from finvestor.core.settings import settings

database = databases.Database(settings.DATABASE_URI)
engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
