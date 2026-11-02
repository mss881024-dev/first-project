"""
BigBang 2026 콘서트 취소표 모니터링 대시보드 — 백엔드
- 입력: 사용자가 직접 붙여넣은 카톡 텍스트 / 업로드한 이미지만 허용
- 예매 사이트 자동화, 카톡 자동 수집, 시간 예측 기능 없음
"""

import os
import re
import json
import base64
import hashlib
import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path

import anthropic
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── 경로 설정 ─────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DB_PATH  = BASE_DIR / "data" / "tickets.db"

# ── DB 초기화 ─────────────────────────────────────────────────────────
def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id          TEXT PRIMARY KEY,
            section     TEXT,
            seat        TEXT,
            concert_date TEXT,
            status      TEXT,
            report_count INTEGER DEFAULT 1,
            raw_text    TEXT,
            first_seen  TEXT,
            last_updated TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS review_queue (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text   TEXT,
            reason     TEXT,
            added_at   TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ── Anthropic 클라이언트 ──────────────────────────────────────────────
def get_anthropic():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    return anthropic.Anthropic(api_key=api_key)

# ── FastAPI 앱 ────────────────────────────────────────────────────────
app = FastAPI(title="취소표 대시보드")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# ── 프롬프트 ─────────────────────────────────────────────────────────
PARSE_SYSTEM = """
너는 빅뱅 2026 콘서트(고양종합운동장, 공연일: 8/21·8/22·8/23) 취소표 정보를 추출하는 파서야.
입력은 카카오톡 PC버전에서 복사한 대화 원문 또는 OCR 텍스트다.

다음 규칙을 엄격히 따라:
1. 좌석/구역 관련 메시지만 추출하고, 나머지는 무시한다.
2. 상태 분류:
   - "취소됨": "취소", "빠짐", "취소됨", "캔슬" 포함 시
   - "재오픈됨": "풀림", "떴다", "재오픈", "다시 나옴", "잡았다" 포함 시
   - "확인필요": 위 어느 것도 해당 안 되거나 모호할 때
3. 닉네임은 절대 포함하지 않는다.
4. 시간 예측·확률·추정치는 절대 생성하지 않는다.
5. 구역 코드: F(플로어석), S(스탠딩), W(서쪽), E(동쪽), N(북쪽), R/S/A(등급), 숫자 조합 등
6. 공연일이 명시되지 않은 경우 concert_date는 null.

출력은 반드시 JSON 배열:
[
  {
    "section": "구역코드 또는 등급 (예: F1, 001, R석, 플로어)",
    "seat": "열-번호 (예: A-12, 없으면 null)",
    "concert_date": "8/21 | 8/22 | 8/23 | null",
    "status": "취소됨 | 재오픈됨 | 확인필요",
    "raw_text": "해당 메시지 원문 (50자 이내, 닉네임 제외)"
  }
]

좌석/구역 언급이 전혀 없으면 빈 배열 []을 반환.
"""

# ── 파싱 함수 ─────────────────────────────────────────────────────────
def call_anthropic_text(client: anthropic.Anthropic, text: str) -> list[dict]:
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=PARSE_SYSTEM,
        messages=[{"role": "user", "content": text}]
    )
    raw = msg.content[0].text.strip()
    # JSON 블록 추출
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    return json.loads(m.group(0)) if m else []


def call_anthropic_image(client: anthropic.Anthropic, img_bytes: bytes, media_type: str) -> list[dict]:
    b64 = base64.standard_b64encode(img_bytes).decode()
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=PARSE_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": b64}
                },
                {"type": "text", "text": "이 카카오톡 스크린샷에서 취소표 정보를 추출해."}
            ]
        }]
    )
    raw = msg.content[0].text.strip()
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    return json.loads(m.group(0)) if m else []


# ── DB 헬퍼 ──────────────────────────────────────────────────────────
def make_ticket_id(section: str, seat: str | None, concert_date: str | None) -> str:
    key = f"{(section or '').upper()}|{(seat or '').upper()}|{concert_date or ''}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def upsert_ticket(item: dict):
    tid  = make_ticket_id(item["section"], item.get("seat"), item.get("concert_date"))
    now  = datetime.now().isoformat(timespec="seconds")
    conn = sqlite3.connect(DB_PATH)
    row  = conn.execute("SELECT status, report_count FROM tickets WHERE id=?", (tid,)).fetchone()

    if row:
        existing_status, cnt = row
        new_status = item["status"]
        # 재오픈 보고가 오면 상태 갱신, 그 외 취소됨은 유지
        if existing_status == "취소됨" and new_status == "재오픈됨":
            final_status = "재오픈됨"
        elif existing_status == "재오픈됨":
            final_status = "재오픈됨"
        else:
            final_status = new_status if new_status != "확인필요" else existing_status
        conn.execute(
            "UPDATE tickets SET status=?, report_count=?, last_updated=? WHERE id=?",
            (final_status, cnt + 1, now, tid)
        )
    else:
        conn.execute(
            "INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?)",
            (tid,
             item.get("section"),
             item.get("seat"),
             item.get("concert_date"),
             item["status"],
             1,
             item.get("raw_text", "")[:100],
             now, now)
        )
    conn.commit()
    conn.close()


def add_review_queue(raw_text: str, reason: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO review_queue (raw_text, reason, added_at) VALUES (?,?,?)",
        (raw_text[:200], reason, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()


def get_all_tickets():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id,section,seat,concert_date,status,report_count,raw_text,first_seen,last_updated "
        "FROM tickets ORDER BY last_updated DESC"
    ).fetchall()
    conn.close()
    keys = ["id","section","seat","concert_date","status","report_count","raw_text","first_seen","last_updated"]
    return [dict(zip(keys, r)) for r in rows]


def get_review_queue():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, raw_text, reason, added_at FROM review_queue ORDER BY added_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [{"id": r[0], "raw_text": r[1], "reason": r[2], "added_at": r[3]} for r in rows]


def delete_review_item(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM review_queue WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


# ── 라우트 ────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root():
    html = (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


class TextInput(BaseModel):
    text: str


@app.post("/api/parse-text")
async def parse_text(body: TextInput):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="텍스트가 비어 있습니다.")
    client = get_anthropic()
    items  = call_anthropic_text(client, body.text)
    saved, review = 0, 0
    for item in items:
        if not item.get("section"):
            add_review_queue(item.get("raw_text", body.text[:100]), "구역 정보 없음")
            review += 1
        else:
            upsert_ticket(item)
            saved += 1
    return {"saved": saved, "review": review, "total_parsed": len(items)}


@app.post("/api/parse-image")
async def parse_image(file: UploadFile = File(...)):
    allowed = {"image/png": "image/png", "image/jpeg": "image/jpeg", "image/jpg": "image/jpeg", "image/webp": "image/webp"}
    media_type = allowed.get(file.content_type)
    if not media_type:
        raise HTTPException(status_code=400, detail="PNG/JPG/WEBP 이미지만 허용됩니다.")
    img_bytes = await file.read()
    client    = get_anthropic()
    items     = call_anthropic_image(client, img_bytes, media_type)
    saved, review = 0, 0
    for item in items:
        if not item.get("section"):
            add_review_queue(item.get("raw_text", f"[이미지:{file.filename}]"), "구역 정보 없음")
            review += 1
        else:
            upsert_ticket(item)
            saved += 1
    return {"saved": saved, "review": review, "total_parsed": len(items)}


@app.get("/api/tickets")
async def list_tickets():
    return get_all_tickets()


@app.delete("/api/tickets/{ticket_id}")
async def delete_ticket(ticket_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/api/review")
async def list_review():
    return get_review_queue()


@app.delete("/api/review/{item_id}")
async def dismiss_review(item_id: int):
    delete_review_item(item_id)
    return {"ok": True}


@app.get("/api/stats")
async def stats():
    tickets = get_all_tickets()
    waiting   = [t for t in tickets if t["status"] == "취소됨"]
    reopened  = [t for t in tickets if t["status"] == "재오픈됨"]
    pending   = [t for t in tickets if t["status"] == "확인필요"]

    section_counts: dict[str, int] = {}
    for t in waiting:
        s = t["section"] or "미상"
        section_counts[s] = section_counts.get(s, 0) + 1

    return {
        "total": len(tickets),
        "waiting": len(waiting),
        "reopened": len(reopened),
        "pending": len(pending),
        "section_counts": section_counts,
    }
