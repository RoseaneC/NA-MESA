import json
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Session as SessionModel
from ..schemas import ChatRequest, ChatResponse, SessionSchema
from ..services.state_machine import handle_message

router = APIRouter()
logger = logging.getLogger("vexia.chat")


def load_context(model: SessionModel):
    try:
        return json.loads(model.context or "{}")
    except json.JSONDecodeError:
        return {}


@router.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    if payload.message is None:
        payload.message = ""

    session_model = None
    if payload.session_id:
        session_model = db.get(SessionModel, payload.session_id)

    if not session_model:
        session_model = SessionModel(
            id=payload.session_id or str(uuid.uuid4()), state="MENU", context="{}"
        )
        db.add(session_model)
        db.commit()
        db.refresh(session_model)

    previous_state = session_model.state
    context = load_context(session_model)

    reply, quick_replies, new_state, new_context = handle_message(
        session_model.state, context, payload.message or ""
    )

    session_model.state = new_state
    session_model.context = json.dumps(new_context or {})
    db.add(session_model)
    db.commit()
    db.refresh(session_model)

    logger.info(
        "session=%s state_from=%s state_to=%s message=%s",
        session_model.id,
        previous_state,
        new_state,
        payload.message,
    )

    return ChatResponse(
        session_id=session_model.id,
        reply=reply,
        quick_replies=quick_replies,
        state=new_state,
        context=new_context or {},
    )


@router.post("/api/reset", response_model=ChatResponse)
def reset_session(payload: ChatRequest, db: Session = Depends(get_db)):
    session_model = None
    if payload.session_id:
        session_model = db.get(SessionModel, payload.session_id)
    if not session_model:
        session_model = SessionModel(id=payload.session_id or str(uuid.uuid4()))
        db.add(session_model)

    session_model.state = "MENU"
    session_model.context = json.dumps({})
    db.add(session_model)
    db.commit()
    db.refresh(session_model)

    reply, quick_replies, state, context = handle_message("MENU", {}, "")
    logger.info("session=%s reset to MENU", session_model.id)

    return ChatResponse(
        session_id=session_model.id,
        reply=reply,
        quick_replies=quick_replies,
        state=state,
        context=context,
    )


@router.get("/api/session/{session_id}", response_model=SessionSchema)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session_model = db.get(SessionModel, session_id)
    if not session_model:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return SessionSchema(
        id=session_model.id,
        state=session_model.state,
        context=load_context(session_model),
    )

