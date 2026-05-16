from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from event_api.routes import router

app = FastAPI(title="QuickCart Event Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def health_check():
    return {
        "status": "QuickCart Event Gateway Running"
    }