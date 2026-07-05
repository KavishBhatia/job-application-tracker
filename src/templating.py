from pathlib import Path

from fastapi.templating import Jinja2Templates

from src.lifecycle import auto_shutdown_enabled

BASE_DIR = Path(__file__).resolve().parent


def _lifecycle_context(request):
    return {"auto_shutdown_enabled": auto_shutdown_enabled()}


templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates"), context_processors=[_lifecycle_context]
)
