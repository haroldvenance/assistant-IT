from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from sqlalchemy.orm import Session
import markdown

from ..database import get_db
from ..models import User, Conversation
from ..auth import get_current_user
from ..utils.pdf_generator import generate_conversation_pdf

router = APIRouter(prefix="/conversations", tags=["Export"])

@router.get("/{conv_id}/export")
def export_conversation(
    conv_id: int,
    format: str = "markdown",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    messages = conv.messages

    if format == "markdown":
        md = f"# {conv.title}\n\n"
        for msg in messages:
            md += f"**{msg.role.capitalize()}** ({msg.created_at.strftime('%Y-%m-%d %H:%M')}):\n{msg.content}\n\n"
        return PlainTextResponse(content=md, media_type="text/markdown; charset=utf-8")

    elif format == "html":
        md = f"# {conv.title}\n\n"
        for msg in messages:
            md += f"**{msg.role.capitalize()}** ({msg.created_at.strftime('%Y-%m-%d %H:%M')}):\n{msg.content}\n\n"
        html = markdown.markdown(md)
        return HTMLResponse(content=f"<html><body>{html}</body></html>")

    elif format == "pdf":
        pdf_path = f"/tmp/conversation_{conv_id}.pdf"
        generate_conversation_pdf(messages, conv.title, pdf_path)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"conversation_{conv_id}.pdf"
        )

    else:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez markdown, html ou pdf.")