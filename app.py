from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Lazy load rembg to reduce startup time
_remove_bg = None

def get_remove_bg():
    global _remove_bg
    if _remove_bg is None:
        from rembg import remove
        _remove_bg = remove
    return _remove_bg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        img = Image.open(file.stream).convert('RGBA')
        
        max_dim = 1500
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        remove_fn = get_remove_bg()
        output = remove_fn(img)
        
        buf = io.BytesIO()
        output.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        
        return jsonify({'image': img_base64})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/apply-effects', methods=['POST'])
def apply_effects():
    try:
        data = request.json
        img_data = base64.b64decode(data['image'])
        img = Image.open(io.BytesIO(img_data)).convert('RGBA')
        
        if data.get('bgType') == 'color':
            bg = Image.new('RGBA', img.size, data['bgColor'])
            bg.paste(img, (0, 0), img)
            img = bg
        
        if data.get('brightness', 1.0) != 1.0:
            img = ImageEnhance.Brightness(img).enhance(data['brightness'])
        if data.get('contrast', 1.0) != 1.0:
            img = ImageEnhance.Contrast(img).enhance(data['contrast'])
        if data.get('sharpness', 1.0) != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(data['sharpness'])
        if data.get('blur'):
            img = img.filter(ImageFilter.SMOOTH)
        
        buf = io.BytesIO()
        img.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        
        return jsonify({'image': img_base64})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
