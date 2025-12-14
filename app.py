import base64
import io
from typing import Any, Dict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from ultralytics import YOLO

from classes_rus import CLASS_MAPPING

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

HEALTHY_CLASSES = {
    'Apple leaf', 'Bell_pepper leaf', 'Blueberry leaf', 'Cherry leaf', 
    'Peach leaf', 'Potato leaf', 'Raspberry leaf', 'Soyabean leaf', 
    'Strawberry leaf', 'Tomato leaf', 'grape leaf'
}

@app.get("/", tags=["Статус"])
def read_root():
    return {"status": "ok", "message": "Сервис классификации болезней растений запущен."}


@app.post("/predict", tags=["Детекция"], response_model=Dict[str, Any])
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
        result = results[0]

        recommendations = "Признаки болезней или вредителей не обнаружены. Продолжайте стандартный уход."
        
        best_disease_label_en = None
        best_disease_conf = 0.0

        if result.boxes and len(result.boxes) > 0:
            
            for box in result.boxes:
                class_index = int(box.cls[0])
                confidence = float(box.conf[0])
                
                label_en = result.names[class_index]
                
                if label_en not in HEALTHY_CLASSES and confidence > best_disease_conf:
                    best_disease_conf = confidence
                    best_disease_label_en = label_en
        
        if best_disease_label_en:
            disease_name_rus = CLASS_MAPPING.get(best_disease_label_en, best_disease_label_en)
            
            try:
                recommendations = 'gigachat отключен'


            except Exception as llm_e:
                recommendations = f"Обнаружена проблема: {disease_name_rus}. Не удалось получить рекомендации от LLM: {llm_e}"

        res_plotted = result.plot()
        res_plotted_rgb = res_plotted[..., ::-1]
        res_image = Image.fromarray(res_plotted_rgb)

        img_io = io.BytesIO()
        res_image.save(img_io, 'JPEG', quality=90)
        img_io.seek(0)


        img_base64 = base64.b64encode(img_io.read()).decode('utf-8')

        return {
            "image_base64": img_base64,
            "media_type": "image/jpeg",
            "recommendations": recommendations,
            "detected_problem": disease_name_rus if best_disease_label_en else "Здоровое растение",
            "status": "success"
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки изображения сервером: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
