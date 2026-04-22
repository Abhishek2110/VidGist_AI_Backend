import os
from fastapi import Depends, FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import transcribe_audio, split_text, clean_filename
from vector_db import create_collection, store_embeddings, search
import uuid
from agents import multi_agent_pipeline
from database import SessionLocal
from models import Chat, Message
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 30 * 1024 * 1024

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):

    video_id = str(uuid.uuid4())
    user_id = "6192f9bd-b8fc-421e-b8a7-b7539cef7842"
    video_path = None

    try:
        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 30MB)")

        clean_name = clean_filename(file.filename)
        video_path = os.path.join(UPLOAD_DIR, clean_name)

        with open(video_path, "wb") as f:
            f.write(contents)

        transcript = transcribe_audio(video_path)

        create_collection()
        chunks = split_text(transcript)
        store_embeddings(chunks, video_id)

        # 🧠 CREATE CHAT ENTRY
        chat = Chat(
            user_id=user_id,
            video_id=video_id,
            title=clean_name,
            transcript=transcript
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

        return {
            "video_id": video_id,
            "chat_id": str(chat.id),
            "filename": clean_name,
            "transcript": transcript
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
            

@app.get("/search")
def search_query(q: str):
    try:
        results = search(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask")
def ask_question(q: str, video_id: str, chat_id: str, db: Session = Depends(get_db)):
    try:

        # 🧠 Save user message
        user_msg = Message(
            chat_id=chat_id,
            role="user",
            content=q
        )
        db.add(user_msg)

        # 🔥 Generate answer
        answer = multi_agent_pipeline(q, video_id)

        # 🧠 Save assistant message
        bot_msg = Message(
            chat_id=chat_id,
            role="assistant",
            content=answer
        )
        db.add(bot_msg)

        db.commit()

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/chat/list")
def get_chats(db: Session = Depends(get_db)):
    user_id = "6192f9bd-b8fc-421e-b8a7-b7539cef7842"

    chats = db.query(Chat)\
        .filter(Chat.user_id == user_id)\
        .order_by(Chat.created_at.desc())\
        .all()
        
    return [
        {
            "chat_id": str(chat.id),
            "video_id": chat.video_id,
            "title": chat.title
        }
        for chat in chats
    ]
    
    
@app.get("/chat/{chat_id}")
def get_messages(chat_id: str, db: Session = Depends(get_db)):
    
    # ✅ Fetch chat
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # ✅ Fetch messages
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()

    return {
        "messages": [
            {
                "role": msg.role,
                "content": msg.content
            } for msg in messages
        ],
        "transcript": chat.transcript
    }  