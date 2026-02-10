let originalImage = null;
let processedImage = null;
let originalFileName = 'image';

const imageInput = document.getElementById('imageInput');
const uploadSection = document.getElementById('uploadSection');
const workspace = document.getElementById('workspace');
const originalImg = document.getElementById('originalImage');
const resultImg = document.getElementById('resultImage');
const loader = document.getElementById('loader');
const removeBtn = document.getElementById('removeBtn');
const controls = document.getElementById('controls');
const downloadSection = document.getElementById('downloadSection');

// File upload
imageInput.addEventListener('change', handleFileSelect);

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    originalFileName = file.name.replace(/\.[^/.]+$/, '');
    
    if (file.size > 100 * 1024 * 1024) {
        alert('File size exceeds 100MB limit');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        originalImage = e.target.result;
        originalImg.src = originalImage;
        uploadSection.style.display = 'none';
        workspace.style.display = 'grid';
    };
    reader.readAsDataURL(file);
}

// Remove background
removeBtn.addEventListener('click', async () => {
    loader.style.display = 'block';
    removeBtn.disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);
        
        const response = await fetch('/remove-bg', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        processedImage = 'data:image/png;base64,' + data.image;
        resultImg.src = processedImage;
        document.getElementById('applyBtn').style.display = 'block';
        downloadSection.style.display = 'block';
        
    } catch (error) {
        alert('Error processing image: ' + error.message);
        console.error('Error:', error);
    } finally {
        loader.style.display = 'none';
        removeBtn.disabled = false;
    }
});

// Background type change
document.getElementById('bgType').addEventListener('change', (e) => {
    document.getElementById('colorPicker').style.display = 
        e.target.value === 'color' ? 'block' : 'none';
    document.getElementById('customBgPicker').style.display = 
        e.target.value === 'custom' ? 'block' : 'none';
});

// Slider updates
document.getElementById('brightness').addEventListener('input', (e) => {
    document.getElementById('brightnessVal').textContent = e.target.value;
});

document.getElementById('contrast').addEventListener('input', (e) => {
    document.getElementById('contrastVal').textContent = e.target.value;
});

document.getElementById('sharpness').addEventListener('input', (e) => {
    document.getElementById('sharpnessVal').textContent = e.target.value;
});

// Apply effects
document.getElementById('applyBtn').addEventListener('click', async () => {
    if (!processedImage) return;
    
    loader.style.display = 'block';
    
    try {
        const base64Data = processedImage.split(',')[1];
        const bgType = document.getElementById('bgType').value;
        
        let customBgData = null;
        if (bgType === 'custom') {
            const customBgFile = document.getElementById('customBg').files[0];
            if (customBgFile) {
                customBgData = await new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onload = (e) => resolve(e.target.result.split(',')[1]);
                    reader.readAsDataURL(customBgFile);
                });
            }
        }
        
        const response = await fetch('/apply-effects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: base64Data,
                bgType: bgType,
                bgColor: document.getElementById('bgColor').value,
                customBg: customBgData,
                brightness: parseFloat(document.getElementById('brightness').value),
                contrast: parseFloat(document.getElementById('contrast').value),
                sharpness: parseFloat(document.getElementById('sharpness').value),
                blur: document.getElementById('blur').checked
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        resultImg.src = 'data:image/png;base64,' + data.image;
        
    } catch (error) {
        alert('Error applying effects: ' + error.message);
        console.error('Error:', error);
    } finally {
        loader.style.display = 'none';
    }
});

// Download buttons
document.getElementById('downloadPng').addEventListener('click', () => {
    downloadImage(resultImg.src, originalFileName + '.png');
});

document.getElementById('downloadJpg').addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        downloadImage(canvas.toDataURL('image/jpeg', 0.95), originalFileName + '.jpg');
    };
    
    img.src = resultImg.src;
});

// New file button
document.getElementById('newFileBtn').addEventListener('click', () => {
    location.reload();
});

function downloadImage(dataUrl, filename) {
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
