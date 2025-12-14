const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('image-preview');
const settingsBox = document.querySelector('.setting-box');
const predictButton = document.getElementById('predictButton');
const resultBox = document.querySelector('.result-box');
const rangeInput = document.getElementById('confidenceRange');
const rangeValue = document.getElementById('rangeValue');
const resultImage = document.getElementById('resultImage');
const uploadLabel = document.querySelector('.upload-label');

document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('confidenceRange');
    const defaultValue = 95;

    slider.value = defaultValue; 
    document.getElementById('rangeValue').textContent = defaultValue;

    console.log("Порог уверенности сброшен до:", slider.value);
});

imageInput.addEventListener('change', function() {
    const file = this.files[0];
    
    if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            uploadLabel.style.display = 'none';
            
            revealElement(settingsBox);
            revealElement(predictButton);
            predictButton.disabled = false;
            
            resultBox.classList.add('hide');
        }
        
        reader.readAsDataURL(file);
    }
});

rangeInput.addEventListener('input', function() {
    rangeValue.textContent = this.value + '%';
});

function revealElement(element) {
    if (element.classList.contains('hide')) {
        element.classList.remove('hide');
        element.classList.add('fade-in-up');
    }
}

async function uploadImage() {
    const file = imageInput.files[0];
    if (!file) return;

    predictButton.textContent = "Обработка...";
    predictButton.disabled = true;

    const formData = new FormData();
    formData.append('file', file);
    const confidenceFloat = rangeInput.value / 100;
    formData.append('conf', confidenceFloat);

    try {
        const response = await axios.post('http://127.0.0.1:8000/predict', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        const data = response.data; 

        const imageUrl = `data:${data.media_type};base64,${data.image_base64}`;
        
        const resultImgTag = document.getElementById('result-image-display');
        resultImgTag.src = imageUrl;
        resultImgTag.style.display = 'block';
        
        revealElement(resultBox);
        
        document.getElementById('diagnosis').textContent = data.detected_problem; 
        
        document.getElementById('confidence').textContent = rangeInput.value + "% (Порог)"; 
        
        document.getElementById('recommendations-text').textContent = data.recommendations;

    } catch (error) {
        console.error(error.response?.data || error);
        alert("Ошибка при обработке: " + (error.response?.data?.detail || "Сервер недоступен"));
    } finally {
        predictButton.textContent = "Получить Диагноз";
        predictButton.disabled = false;
    }
}
