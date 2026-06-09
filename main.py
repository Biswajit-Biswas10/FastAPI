from fastapi import FastAPI, Request, status
from models import Base
from database import engine
from routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from logging_config import setup_logging, get_logger
from monitoring import setup_monitoring

setup_logging()
logger = get_logger(__name__)

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Attach Prometheus monitoring
setup_monitoring(app)

app.mount("/static", StaticFiles(directory="routers/static"), name="static")

logger.info("TodoApp started successfully")


@app.get("/")
def root(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


@app.api_route("/healthy", methods=["GET", "HEAD"])
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

logger.info("All routers registered, monitoring active at /metrics")