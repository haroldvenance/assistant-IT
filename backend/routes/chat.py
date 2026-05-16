from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
from datetime import datetime

from ..database import get_db, SessionLocal
from ..models import User, Conversation, Message
from ..schemas import ChatRequest
from ..auth import get_current_user
from ..config import AVAILABLE_MODELS
from ..services.llm import call_groq, call_groq_stream, LLMServiceError
from ..services.summary import manage_context_window
from ..middleware.rate_limiter import limiter

router = APIRouter(tags=["Chat"])

SYSTEM_PROMPT = (
    "Tu es un assistant expert en informatique (systèmes, réseaux, dépannage). "
    "Réponds de façon claire, précise et pédagogique."
)

def build_api_messages(conv: Conversation, new_message: str) -> list:
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conv.messages:
        api_messages.append({"role": msg.role, "content": msg.content})
    api_messages.append({"role": "user", "content": new_message})
    return api_messages

@router.post("/chat")
@limiter.limit("25/minute")
async def chat(
    request: Request,
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == req.conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    if req.model not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail="Modèle non supporté")

    api_messages = build_api_messages(conv, req.message)
    api_messages = await manage_context_window(api_messages, req.model)

    user_msg = Message(conversation_id=conv.id, role="user", content=req.message)
    db.add(user_msg)
    conv.updated_at = datetime.utcnow()
    db.commit()

    try:
        assistant_content = await call_groq(api_messages, req.model)
    except LLMServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    assistant_msg = Message(conversation_id=conv.id, role="assistant", content=assistant_content)
    db.add(assistant_msg)
    conv.updated_at = datetime.utcnow()
    db.commit()

    return {"response": assistant_content}

@router.post("/chat/stream")
@limiter.limit("25/minute")
async def chat_stream(
    request: Request,
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == req.conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    if req.model not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail="Modèle non supporté")

    api_messages = build_api_messages(conv, req.message)
    api_messages = await manage_context_window(api_messages, req.model)

    # Sauvegarde immédiate du message utilisateur
    user_msg = Message(conversation_id=conv.id, role="user", content=req.message)
    db.add(user_msg)
    conv.updated_at = datetime.utcnow()
    db.commit()

    # Extraire l'ID avant de quitter la session
    conv_id = conv.id

    async def event_stream():
        full_response = ""
        try:
            async for token in call_groq_stream(api_messages, req.model):
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except LLMServiceError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        # Sauvegarde du message assistant dans une nouvelle session
        new_db = SessionLocal()
        try:
            assistant_msg = Message(conversation_id=conv_id, role="assistant", content=full_response)
            new_db.add(assistant_msg)
            # Mise à jour de la date de la conversation
            conv_to_update = new_db.query(Conversation).filter(Conversation.id == conv_id).first()
            if conv_to_update:
                conv_to_update.updated_at = datetime.utcnow()
            new_db.commit()
        except Exception as e:
            new_db.rollback()
            print(f"Erreur sauvegarde stream: {e}")
        finally:
            new_db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")