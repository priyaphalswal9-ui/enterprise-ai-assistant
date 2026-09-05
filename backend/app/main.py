from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Enterprise AI Assistant API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}