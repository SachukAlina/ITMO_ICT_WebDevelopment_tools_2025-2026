from fastapi import FastAPI, HTTPException, status
from models import Author, LibraryEntry

app = FastAPI(title="BookCrossing — practice 1.1")

temp_library: list[dict] = [
    {
        "id": 1,
        "owner": {"id": 1, "username": "alina", "full_name": "Alina Sachuk"},
        "book": {
            "id": 1,
            "title": "The Little Prince",
            "authors": [{"id": 1, "name": "Antoine de Saint-Exupéry"}],
        },
        "condition": "good",
        "notes": "Available for exchange",
    },
    {
        "id": 2,
        "owner": {"id": 2, "username": "reader", "full_name": "Test Reader"},
        "book": {
            "id": 2,
            "title": "Pride and Prejudice",
            "authors": [{"id": 2, "name": "Jane Austen"}],
        },
        "condition": "worn",
        "notes": None,
    },
]


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "BookCrossing practice API"}


@app.get("/library", response_model=list[LibraryEntry])
def list_entries() -> list[dict]:
    return temp_library


@app.get("/library/{entry_id}", response_model=LibraryEntry)
def get_entry(entry_id: int) -> dict:
    for entry in temp_library:
        if entry["id"] == entry_id:
            return entry
    raise HTTPException(status_code=404, detail="Library entry not found")


@app.post("/library", response_model=LibraryEntry, status_code=status.HTTP_201_CREATED)
def create_entry(entry: LibraryEntry) -> LibraryEntry:
    if any(item["id"] == entry.id for item in temp_library):
        raise HTTPException(status_code=409, detail="Entry already exists")
    temp_library.append(entry.model_dump())
    return entry


@app.put("/library/{entry_id}", response_model=LibraryEntry)
def replace_entry(entry_id: int, entry: LibraryEntry) -> LibraryEntry:
    for index, current in enumerate(temp_library):
        if current["id"] == entry_id:
            replacement = entry.model_copy(update={"id": entry_id})
            temp_library[index] = replacement.model_dump()
            return replacement
    raise HTTPException(status_code=404, detail="Library entry not found")


@app.delete("/library/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int) -> None:
    for index, entry in enumerate(temp_library):
        if entry["id"] == entry_id:
            temp_library.pop(index)
            return
    raise HTTPException(status_code=404, detail="Library entry not found")


@app.get("/authors", response_model=list[Author])
def list_authors() -> list[Author]:
    authors: dict[int, Author] = {}
    for entry in temp_library:
        for raw_author in entry["book"]["authors"]:
            author = Author.model_validate(raw_author)
            authors[author.id] = author
    return list(authors.values())


@app.post("/authors", response_model=Author, status_code=status.HTTP_201_CREATED)
def create_nested_author(entry_id: int, author: Author) -> Author:
    entry = next((item for item in temp_library if item["id"] == entry_id), None)
    if entry is None:
        raise HTTPException(status_code=404, detail="Library entry not found")
    entry["book"]["authors"].append(author.model_dump())
    return author
