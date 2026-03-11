"""
Claude API Proxy для Mini App
==============================
Приймає запити від браузера, передає до Anthropic API.
Ключ CLAUDE_API_KEY зберігається тільки на сервері.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import anthropic

app = FastAPI()

# CORS — дозволяємо запити з GitHub Pages і будь-якого origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SYSTEM_PROMPT = """Ти — теплий, уважний AI-помічник психолога Олени Коваленко.
Відповідаєш ТІЛЬКИ українською мовою.

Твоя роль:
- Надавати емоційну підтримку та розуміння
- Допомагати людині краще зрозуміти свій стан
- Задавати м'які уточнюючі запитання
- Ніколи не ставити діагнозів і не замінювати живого психолога

Стиль:
- Тепло і без осуду
- Коротко (3-5 речень максимум)
- Іноді завершуй відповідь одним м'яким запитанням
- Якщо людина в кризі — м'яко направляй до запису на консультацію

Заборонено:
- Медичні поради і діагнози
- Теми не пов'язані з психологічним станом
- Давати конкретні техніки і вправи (це робота живого психолога)"""


class Message(BaseModel):
    role: str  # "user" або "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


@app.post("/chat")
async def chat(req: ChatRequest):
    if not CLAUDE_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")

    # Беремо останні 10 повідомлень щоб не виходити за ліміт
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


@app.get("/health")
def health():
    return {"status": "ok"}
