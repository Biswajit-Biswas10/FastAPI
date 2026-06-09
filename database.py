"""
database.py - Database Configuration Layer

Responsible for:
- Defining the database connection URL (SQLite for development)
- Creating the SQLAlchemy engine (the connection pool to the database)
- Configuring the session factory (SessionLocal) for creating database sessions
- Creating the declarative Base class that all models inherit from

This file is imported by models.py (for Base) and by routers/todos.py (for SessionLocal).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base



# Prod Database
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_lfDqR7oBdr9s@ep-empty-shape-aqdb8xiv-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)



# SQLite URL from database.py (Lesson 153)
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db" 
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:test1234@localhost/TodoApplicationDatabase" # This one is for PostgreSQL

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Biswa.Sharmi25#@127.0.0.1:3306/TodoApplicationDatabase"  # This is for MySQL

# SQLite restricts connections to the creating thread by default.
# check_same_thread=False is required because FastAPI serves requests across multiple threads.
# Remove connect_args entirely when switching to PostgreSQL.


"""
# This is for SQLite only
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
"""



# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session factory — each call to SessionLocal() opens a new database session.
# autocommit=False: changes require an explicit session.commit()
# autoflush=False: pending changes aren't pushed to the DB before every query
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models. Every class inheriting from Base
# is registered in Base.metadata and can be materialised as a database table.
Base = declarative_base()

