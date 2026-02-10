from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

_remove_bg = None

def get_remove_bg():
    global _remove_bg
    if _remove_bg is None:
        try:
            from rembg import remove
            _remove_bg = remove
            logger.info("rembg loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load rembg: {e}")
            raise
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
        logger.info("Remove background request received")
        
        if 'image' not in request.files:
            logger.error("No image in request")
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        logger.info(f"Processing image: {file.filename}")
        
        img = Image.open(file.stream).convert('RGBA')
        logger.info(f"Image size: {img.size}")
        
        max_dim = 1500
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Resized to: {new_size}")
        
        remove_fn = get_remove_bg()
        output = remove_fn(img)
        logger.info("Background removed")
        
        buf = io.BytesIO()
        output.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        
        logger.info("Image encoded successfully")
        return jsonify({'image': img_base64})
    
    except Exception as e:
        logger.error(f"Error in remove_background: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/apply-effects', methods=['POST'])
def apply_effects():
    try:
        logger.info("Apply effects request received")
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
        
        logger.info("Effects applied successfully")
        return jsonify({'image': img_base64})
    
    except Exception as e:
        logger.error(f"Error in apply_effects: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
