from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageEnhance, ImageFilter, ImageChops
import io
import base64
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def simple_remove_bg(img):
    """Simple background removal using edge detection and color analysis"""
    try:
        # Convert to RGB for processing
        rgb_img = img.convert('RGB')
        
        # Get image data
        pixels = rgb_img.load()
        width, height = rgb_img.size
        
        # Sample corner pixels to determine background color
        corners = [
            pixels[0, 0],
            pixels[width-1, 0],
            pixels[0, height-1],
            pixels[width-1, height-1]
        ]
        
        # Average corner color as background
        bg_color = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
        
        # Create alpha channel
        alpha = Image.new('L', (width, height), 255)
        alpha_pixels = alpha.load()
        
        # Tolerance for color matching
        tolerance = 40
        
        # Remove background
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                # Check if pixel is close to background color
                if (abs(r - bg_color[0]) < tolerance and 
                    abs(g - bg_color[1]) < tolerance and 
                    abs(b - bg_color[2]) < tolerance):
                    alpha_pixels[x, y] = 0
        
        # Apply alpha channel
        result = img.copy()
        result.putalpha(alpha)
        
        return result
    except Exception as e:
        logger.error(f"Error in simple_remove_bg: {e}")
        raise

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
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        img = Image.open(file.stream).convert('RGBA')
        
        max_dim = 1000
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        output = simple_remove_bg(img)
        
        buf = io.BytesIO()
        output.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        
        return jsonify({'image': img_base64})
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
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
        logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
