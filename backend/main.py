from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import User, Conversation
from .schemas import UserOut, ConversationOut
from .auth import require_admin
from .routes import auth, conversations, chat, export
from .middleware.rate_limiter import limiter
from .middleware.error_handler import (
    validation_exception_handler,
    rate_limit_exceeded_handler,
    generic_exception_handler
)

Base.metadata.create_all(bind=engine)

# Désactive la redirection automatique des slashes
app = FastAPI(
    title="IT Support Assistant API",
    version="1.0.0",
    redirect_slashes=False
)

app.state.limiter = limiter
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(export.router)

@app.get("/admin/users", response_model=list[UserOut], tags=["Admin"])
def list_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return db.query(User).all()

@app.get("/admin/conversations", response_model=list[ConversationOut], tags=["Admin"])
def list_all_conversations(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return db.query(Conversation).all()