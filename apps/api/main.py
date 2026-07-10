"""Entrypoint процесса API. Запуск: `python -m apps.api.main` или через uvicorn напрямую.

В Docker-образе используется:
    uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from dealhunter.presentation.api.app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    from dealhunter.core.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "apps.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=not settings.is_production,
    )
