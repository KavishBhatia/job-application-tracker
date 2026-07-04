import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src import db
from src.routes import applications, io
from src.templating import BASE_DIR

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job_application_tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Job Application Tracker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(applications.router)
app.include_router(io.router)
