from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI(title="Notes API", version="1.0.0")

notes = {}


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class Note(BaseModel):
    id: str
    title: str
    content: str


@app.get("/")
def root():
    return {"message": "Notes API is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/notes", response_model=list[Note])
def get_notes():
    return list(notes.values())


@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: NoteCreate):
    note_id = str(uuid.uuid4())
    new_note = Note(id=note_id, title=note.title, content=note.content)
    notes[note_id] = new_note
    return new_note


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: str):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    return notes[note_id]


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, update: NoteUpdate):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    note = notes[note_id]
    if update.title is not None:
        note.title = update.title
    if update.content is not None:
        note.content = update.content
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del notes[note_id]
