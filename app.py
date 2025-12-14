
import os

from fastapi import FastAPI
from ultralytics import YOLO

MODEL_PATH = r"best.pt"

SAVE_DIR = "api_results"
os.makedirs(SAVE_DIR, exist_ok=True)

CONFIDENCE_THRESHOLD = 0.35 


app = FastAPI()

model = YOLO(MODEL_PATH)
print("YOLO модель успешно загружена.")

@app.get("/", tags=["Статус"])
def read_root():
    return {"status": "ok", "message": "Сервис классификации болезней растений запущен."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
