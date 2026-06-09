"""
routers/todos.py - Todo CRUD Routes

Responsible for:
- All todo-related API endpoints (Create, Read, Update, Delete)
- Database session management via the get_db dependency
- Request validation using Pydantic's TodoRequest model
- Endpoints: GET / (all todos), GET /todo/{id}, POST /todo, PUT /todo, DELETE /todo/{id}

This router is registered in main.py via app.include_router(todos.router)
"""

from typing import Annotated
from pydantic import BaseModel, Field


from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from starlette import status
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


from models import Todos
from database import SessionLocal

from .auth import get_current_user # # 130. Added This package

from monitoring import TODO_OPERATIONS, DBMetricsTracker



templates = Jinja2Templates(directory="routers/templates")


router = APIRouter(
    prefix='/todos',
    tags=['todos']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# DB Dependency for Database dependency and user_dependency for authenticate user. 
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)] # 130. Added dependency


# Pydantic request for create a request. and for data validation
class TodoRequest(BaseModel):
    title: str = Field(min_length= 3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool



def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    return redirect_response


### Pages ###
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        return templates.TemplateResponse(name="todo.html", request=request, context={"todos": todos, "user": user})

    except:
        return redirect_to_login()
    


@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(name="add-todo.html", request=request, context={"user": user})

    except:
        return redirect_to_login()
    

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()
        
        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse(name="edit-todo.html", request=request, context={"todo": todo, "user": user})

    except:
        return redirect_to_login()

### Endpoints ###



# End point for returning all data from database
# API endpoint named read all using dependency injection for database
# 131 Code added here to get all todos.
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, 
                   db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()



# Searching data using todo id
# 132. Code added here, get todo by specific ID
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo_by_id(user: user_dependency,
                          db: db_dependency,
                          todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')

# For monitoring
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    with DBMetricsTracker("select"):
        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

    TODO_OPERATIONS.labels(operation="read").inc()
    return todos



# Create a new data
# 130. Added code here
# @router.post("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency, 
                      db: db_dependency, 
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('id'))

    db.add(todo_model)
    db.commit()

# For monitoring
@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    with DBMetricsTracker("insert"):
        db.add(todo_model)
        db.commit()

    TODO_OPERATIONS.labels(operation="create").inc()


# Update an existing data
# 133. Code added here
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
                      user: user_dependency,
                      db: db_dependency, 
                      todo_id: int,
                      todo_request: TodoRequest
                      ):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


# For monitoring
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_id: int, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    with DBMetricsTracker("select"):
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(
            Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    with DBMetricsTracker("update"):
        db.add(todo_model)
        db.commit()

    TODO_OPERATIONS.labels(operation="update").inc()


# Delete request
# 134. Code added here
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency, 
                      todo_id: int = Path(gt=0)):
    
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo Not Found.')
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()

    db.commit()

# For monitoring
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    with DBMetricsTracker("select"):
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(
            Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo Not Found.')

    with DBMetricsTracker("delete"):
        db.query(Todos).filter(Todos.id == todo_id).filter(
            Todos.owner_id == user.get('id')).delete()
        db.commit()

    TODO_OPERATIONS.labels(operation="delete").inc()