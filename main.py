"""
Claude API Proxy для Mini App
==============================
- /chat  -> відповіді Claude
- /notify -> відправка повідомлень у Telegram
"""

import os
import httpx
import anthropic

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List


app = FastAPI()


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------- ENV ----------------

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


# ---------------- SYSTEM PROMPT ----------------

SYSTEM_PROMPT = """Ти — теплий, уважний AI-помічник психолога Олени Коваленко.
Відповідаєш ТІЛЬКИ українською мовою.

Твоя роль:
- Надавати емоційну підтримку
- Допомагати зрозуміти емоційний стан
- Ставити м'які уточнюючі запитання
- Не ставити діагнозів

Стиль:
- Тепло
- Без осуду
- 3–5 речень максимум
- Іноді завершуй питанням

Якщо людині дуже важко — м'яко запропонуй запис на консультацію.
"""


# ---------------- MODELS ----------------

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class NotifyRequest(BaseModel):
    chat_id: str
    text: str


# ---------------- CHAT ENDPOINT ----------------

@app.post("/chat")
async def chat(req: ChatRequest):

    if not CLAUDE_API_KEY:
        raise HTTPException(status_code=500, detail="CLAUDE_API_KEY missing")

    messages = [{"role": m.role, "content": m.content} for m in req.messages[-10:]]

    try:

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=messages,
        )

        return {"reply": response.content[0].text}

    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------------- TELEGRAM NOTIFY ----------------

@app.post("/notify")
async def notify(req: NotifyRequest):

    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN missing")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": req.chat_id,
        "text": req.text,
        "parse_mode": "Markdown"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload)

    data = response.json()

    if not data.get("ok"):
        raise HTTPException(status_code=502, detail=data)

    return {"ok": True}


# ---------------- HEALTH ----------------

@app.get("/health")
def health():
    return {"status": "ok"}
