from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items")
def read_items():
    return {"items": []}

@app.post("/items")
def create_item(item: str):
    return {"item": item}