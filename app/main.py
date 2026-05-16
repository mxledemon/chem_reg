from fastapi import FastAPI
from app.routers import health
from app.routers import molecules
from app.routers import uploads
from app.db import init_db

app = FastAPI(title='ChemREG lite')

app.include_router(health.router)
app.include_router(molecules.router)
app.include_router(uploads.router)

@app.on_event('startup')
def startup():
    init_db()

@app.get('/')
def root():
    return {'message': 'API ChemReg lite is running'}