import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src import db
from src.lifecycle import auto_shutdown_enabled, monitor
from src.routes import applications, io, system
from src.templating import BASE_DIR

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job_application_tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    monitor_task = asyncio.create_task(monitor.run()) if auto_shutdown_enabled() else None
    try:
        yield
    finally:
        if monitor_task:
            monitor_task.cancel()


app = FastAPI(title="Job Application Tracker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(applications.router)
app.include_router(io.router)
app.include_router(system.router)
