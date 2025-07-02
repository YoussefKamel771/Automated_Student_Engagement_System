from fastapi import FastAPI
import uvicorn

app = FastAPI()

# End point for healthy check
@app.get("/", tags=['Home'])
async def home():
    return {'up & running'}


@app.post("/api/v1/engagement/upload", tags=['Engagement'])
async def upload_engagement(data: dict):
    print("Received data:", data)  # For debugging
    return {"status": "success", "message": "Data received"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)