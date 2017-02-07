from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bg_agg import app

engine = create_engine(app.config["DATABASE_URI"], echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()