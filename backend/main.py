from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import engine, Base, seed_database
from routes.chargebacks import router as chargebacks_router
from routes.bank_webhook import router as bank_router

app = FastAPI(title="Representment Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chargebacks_router, prefix="/api")
app.include_router(bank_router, prefix="/api/bank")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_database()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
