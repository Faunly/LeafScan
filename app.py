import io

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image
from ultralytics import YOLO

MODEL_PATH = r"best.pt"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = YOLO(MODEL_PATH)
    print(f"Модель {MODEL_PATH} успешно загружена.")
except Exception as e:
    print(f"Ошибка загрузки модели: {e}")


@app.get("/", tags=["Статус"])
def read_root():
    return {"status": "ok", "message": "Сервис классификации болезней растений запущен."}


@app.post("/predict", tags=["Детекция"])
async def predict_plant_disease(
    file: UploadFile = File(...), 
    conf: float = Form(...)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        results = model(image, conf=conf)

        res_plotted = results[0].plot()
        res_plotted_rgb = res_plotted[..., ::-1]
        res_image = Image.fromarray(res_plotted_rgb)

        img_io = io.BytesIO()
        res_image.save(img_io, 'JPEG', quality=90)
        img_io.seek(0)

        return StreamingResponse(img_io, media_type="image/jpeg")

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обработки изображения сервером.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
