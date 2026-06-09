"""
main.py - Application Entry Point

Responsible for:
- Creating the FastAPI application instance
- Triggering database table creation via models.Base.metadata.create_all()
- Registering all route modules (auth, todos) using app.include_router()

This is the file uvicorn runs: uvicorn main:app --reload
"""

from fastapi import FastAPI, Request, status
from models import Base
from database import engine
from routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


app = FastAPI()

# Creates tables in the database if they don't already exist.
# Runs CREATE TABLE IF NOT EXISTS for every model registered with Base.
Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="routers/static"), name="static")


@app.get("/")
def test(request: Request):
    # return templates.TemplateResponse("home.html", {"request": request})
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

# 164 Added this function
@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


# Register route modules — each router handles its own group of endpoints
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

