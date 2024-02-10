from fastapi import FastAPI
from typing import List

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items")
def read_items():
    return {"items": ["item1", "item2", "item3"]}

@app.post("/items")
def create_item(item: str):
    return {"item": item}

@app.delete("/items")
def delete_items():
    return {"message": "All items deleted"}
