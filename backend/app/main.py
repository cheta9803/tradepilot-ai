# backend application entrypoint

from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'TradePilot AI backend is running'}
