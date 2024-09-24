import uvicorn
from fastapi import FastAPI
from app.api import router

app = FastAPI()
app.include_router(router)

@app.get('/')
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)