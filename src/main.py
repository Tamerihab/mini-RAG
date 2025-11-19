from fastapi import FastAPI
from routes import base

app = FastAPI()

app.include_router(base.router) 

def welcome_message():
    return {"message": "Welcome to the FastAPI application!"}


# @app.get("/")
# async def read_root():
#     return read_root()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

