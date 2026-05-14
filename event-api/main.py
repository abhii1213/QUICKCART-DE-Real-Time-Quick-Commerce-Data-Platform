from fastapi import FastAPI

app = FastAPI(title="QuickCart Event Gateway")


@app.get("/")
def health_check():
    return {"status": "QuickCart Event Gateway Running"}