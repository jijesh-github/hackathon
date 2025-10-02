from fastapi import FastAPI

app = FastAPI(title="Sentiment Analysis API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Sentiment Analysis API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}