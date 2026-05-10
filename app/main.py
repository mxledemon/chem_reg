from fastapi import FastAPI
from app.routers import health
from app.db import init_db

app = FastAPI(title='ChemREG lite')

app.include_router(health.router)

@app.on_event('startup')
def startup():
    init_db()

@app.get('/')
def root():
    return {'message': 'API ChemReg lite is running'}