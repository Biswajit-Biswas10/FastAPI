"""
routers/auth.py - Authentication Routes

Responsible for:
- Handling user authentication and authorization endpoints
- Currently a placeholder with a single GET endpoint
- Will eventually handle user registration, login, JWT token generation, and password hashing

This router is registered in main.py via app.include_router(auth.router)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext

from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

from starlette import status
from datetime import timedelta, datetime, timezone

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Lesson 127
SECRET_KEY = '1418615f908aab44fa586c36b0f43ac6683239a39381030a635f2380d89ffbd5'
ALGORITHM = 'HS256'

# For hashing password
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


# Pydantic Field validation for creating a new user on our application
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="routers/templates")


### Pages ###

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(name="login.html", request=request, context={})

@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse(name="register.html", request=request, context={})

### Endpoints ###


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


# 135. Code added here
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):

    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# 135. Code added here
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail = 'Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail = 'Could not validate user.')



# Create User
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, 
                      create_user_request: CreateUserRequest):

    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        phone_number = create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()



# Delete a user using user_ID, Additionally I have added this code. 
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: db_dependency,
    current_user: Annotated[dict, Depends(get_current_user)],
    user_id: int,
    username: str,
):
    user = db.query(Users).filter(
        Users.id == user_id,
        Users.username == username,
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()




# Validate authentication (Check user that exist in DB)
# 135. Code added here
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

