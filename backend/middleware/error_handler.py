from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
import traceback
import logging

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gère les erreurs de validation des données entrantes."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Données invalides",
            "errors": exc.errors()
        }
    )

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Gère le dépassement du quota de requêtes."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Limite de requêtes atteinte. Veuillez réessayer plus tard."
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Gère toutes les autres exceptions non capturées."""
    # Log l'erreur complète côté serveur
    logger.error(f"Exception non gérée : {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erreur interne du serveur"}
    )