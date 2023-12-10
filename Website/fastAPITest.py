#!/usr/bin/env python3.11
import fastapi
import uvicorn

api = fastapi.FastAPI()

@api.get('/')
def calculate():
    answer = 24 + 18
    return {'answer': answer}

# To test this app locally, uncomment this line:
uvicorn.run(api, host="localhost", port=8000)