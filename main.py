from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import sqlite3
import os
import bcrypt
from pydantic import BaseModel

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Set up static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
def get_db(username: str):
    db_path = f"databases/{username}.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# User model
# class User(BaseModel):
#     username: str
#     password: str

# User verification
def verify_user(username: str, password: str):
    conn = sqlite3.connect('databases/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode('utf-8'), result[0])
    return False

# Routes
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if verify_user(username, password):
        return RedirectResponse(url=f"/flashcards/{username}", status_code=303)
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.get("/flashcards/{username}", response_class=HTMLResponse)
async def flashcards(request: Request, username: str):
    conn = get_db(username)
    cursor = conn.cursor()
    today = datetime.now().date()
    cursor.execute("SELECT * FROM flashcards WHERE review_date <= ? ORDER BY RANDOM() LIMIT 1", (today,))
    flashcard = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM flashcards WHERE review_date <= ?", (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return templates.TemplateResponse("flashcards.html", {"request": request, "flashcard": flashcard, "username": username, "count": count})

@app.post("/answer/{username}/{flashcard_id}")
async def answer(username: str, flashcard_id: int, correct: bool = Form(...)):
    conn = get_db(username)
    cursor = conn.cursor()
    if correct:
        cursor.execute("UPDATE flashcards SET level = level + 1, review_date = ? WHERE id = ?", 
                       (datetime.now().date() + timedelta(days=2**(cursor.execute("SELECT level FROM flashcards WHERE id = ?", (flashcard_id,)).fetchone()[0] ) - 1), flashcard_id))
    else:
        cursor.execute("UPDATE flashcards SET level = 2, review_date = ? WHERE id = ?", 
                       (datetime.now().date() + timedelta(days=1), flashcard_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/flashcards/{username}", status_code=303)

@app.post("/add_flashcard/{username}")
async def add_flashcard(username: str, question: str = Form(...), answer: str = Form(...)):
    conn = get_db(username)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO flashcards (question, answer, review_date, level) VALUES (?, ?, ?, ?)",
                   (question, answer, datetime.now().date() + timedelta(days=0), 2))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/flashcards/{username}", status_code=303)

@app.post("/edit_flashcard/{username}/{flashcard_id}")
async def edit_flashcard(username: str, flashcard_id: int, question: str = Form(...), answer: str = Form(...)):
    conn = get_db(username)
    cursor = conn.cursor()
    cursor.execute("UPDATE flashcards SET question = ?, answer = ? WHERE id = ?", (question, answer, flashcard_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/flashcards/{username}", status_code=303)

@app.post("/delete_flashcard/{username}/{flashcard_id}")
async def delete_flashcard(username: str, flashcard_id: int):
    conn = get_db(username)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/flashcards/{username}", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)