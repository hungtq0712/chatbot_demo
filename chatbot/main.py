from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# --- DB chat ---
from chatbot.db import Base, engine, get_db
from chatbot.models import ChatSession, ChatMessage
from chatbot.schemas import ChatRequest, ChatResponse, SessionOut
from chatbot.responses.message import messages_1
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:63342",
        "http://127.0.0.1:63342",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# tạo bảng nếu chưa có (khi start server)
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Chat bot AI"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    # 1) tạo hoặc lấy session
    if (req.session_id == -1 or req.session_id is None):
        s = ChatSession()
        db.add(s)
        db.commit()
        db.refresh(s)
    else:
        s = db.get(ChatSession, int(req.session_id))

    # 2) lưu message user
    user_msg = ChatMessage(session_id=s.id, role="user", content=req.message)
    db.add(user_msg)

    # 3) tạo reply bot (demo: echo)
    reply_ = f" {messages_1(req.message)}"

    # 4) lưu message bot
    bot_msg = ChatMessage(session_id=s.id, role="bot", content=reply_)
    db.add(bot_msg)

    db.commit()
    return ChatResponse(session_id=s.id, reply=reply_)


@app.get("/session/{session_id}", response_model=SessionOut)
def get_session_history(session_id: int, db: Session = Depends(get_db)):
    s = db.get(ChatSession, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    # lấy messages theo thứ tự thời gian/id
    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )

    s.messages = msgs
    return s


@app.get("/sessions", response_model=list[SessionOut])
def get_all_sessions(db: Session = Depends(get_db)):
    sessions = (
        db.query(ChatSession)
        .order_by(ChatSession.id.desc())
        .all()
    )
    return sessions
@app.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    s = db.get(ChatSession, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(s)
    db.commit()
    return {"detail": "Deleted", "session_id": session_id}



