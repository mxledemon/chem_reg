from fastapi import FastAPI
from app.routers import health

app = FastAPI(title='ChemREG lite')

app.add_route(health.router)

@app.get('/')
def root():
    return {'message': 'API ChemReg lite is running'}