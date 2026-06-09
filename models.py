"""
models.py - Database Table Definitions (ORM Models)

Responsible for:
- Defining the structure of database tables as Python classes
- Each class that inherits from Base maps to a table in the database
- Currently defines the 'todos' table with columns: id, title, description, priority, complete

This file is imported by main.py (to trigger table creation) and by routers/todos.py (for querying).
"""

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey

from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)

class Todos(Base):
    """Represents the 'todos' table in the database.

    Each row is a single todo item with a title, description,
    priority level (1-5), and a completion status.
    """

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

