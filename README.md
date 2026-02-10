# 🖼️ AI Background Remover

Fast, free, and easy-to-use AI-powered background removal tool with custom responsive UI.

## 🌐 Live Demo

**[Try it now: https://w1rd8vpj-5000.inc1.devtunnels.ms/](https://w1rd8vpj-5000.inc1.devtunnels.ms/)**

## ✨ Features

- 🤖 AI-powered background removal
- 🎨 Custom background (solid color)
- ⚙️ Image adjustments (brightness, contrast, sharpness)
- 📥 Download as PNG or JPEG
- 📱 Fully responsive and mobile-friendly
- ⚡ Optimized for high performance
- 🎯 Custom UI (No Streamlit)

## 🚀 Deployment Options

### Option 1: Heroku (Recommended)
```bash
heroku create your-app-name
git push heroku main
```

### Option 2: Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`

### Option 3: Railway
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repo
3. Deploy automatically

### Option 4: PythonAnywhere
1. Upload files
2. Set up WSGI configuration
3. Point to `app.py`

## 📦 Local Installation

```bash
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000

## 🔧 Tech Stack

- **Flask** - Web framework
- **rembg** - AI background removal
- **Pillow** - Image processing
- **HTML/CSS/JS** - Custom responsive UI

## 📝 Features

- Mobile-first responsive design
- Fast loading times
- Optimized images
- SEO meta tags
- No external dependencies for UI
- Works on all devices

## 🌐 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

## 📄 License

MIT License - Free to use and modify
