from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove
import io
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        img = Image.open(file.stream).convert('RGBA')
        
        # Resize if too large
        max_dim = 2000
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Remove background
        output = remove(img)
        
        # Convert to base64
        buf = io.BytesIO()
        output.save(buf, format='PNG')
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
        
        # Apply background
        if data.get('bgType') == 'color':
            bg = Image.new('RGBA', img.size, data['bgColor'])
            bg.paste(img, (0, 0), img)
            img = bg
        
        # Apply adjustments
        if data.get('brightness', 1.0) != 1.0:
            img = ImageEnhance.Brightness(img).enhance(data['brightness'])
        if data.get('contrast', 1.0) != 1.0:
            img = ImageEnhance.Contrast(img).enhance(data['contrast'])
        if data.get('sharpness', 1.0) != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(data['sharpness'])
        if data.get('blur'):
            img = img.filter(ImageFilter.SMOOTH)
        
        # Convert to base64
        buf = io.BytesIO()
        img.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        
        return jsonify({'image': img_base64})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
