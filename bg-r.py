import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove
import io

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Background Remover - Free AI Tool",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI-powered background remover tool. Fast, free, and easy to use."
    }
)

# Custom CSS for mobile responsiveness and performance
st.markdown("""
<style>
    /* Mobile-first responsive design */
    .stApp { max-width: 100%; }
    .stButton>button { width: 100%; }
    @media (max-width: 768px) {
        .stColumns { flex-direction: column; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
    }
    /* Performance optimizations */
    img { image-rendering: -webkit-optimize-contrast; }
    .stImage { will-change: transform; }
</style>
""", unsafe_allow_html=True)

# SEO Meta tags
st.markdown("""
<meta name="description" content="Free AI-powered background remover. Remove image backgrounds instantly with advanced editing tools. No signup required.">
<meta name="keywords" content="background remover, remove background, AI image editor, photo editor, transparent background">
<meta name="author" content="Background Remover Tool">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="Free AI Background Remover">
<meta property="og:description" content="Remove image backgrounds instantly with AI">
<meta property="og:type" content="website">
""", unsafe_allow_html=True)

st.title("🖼️ AI Background Remover")
st.caption("Fast, free, and easy to use. No signup required.")

ALLOWED_TYPES = ["png", "jpg", "jpeg", "webp"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # Reduced to 5MB for better performance

# Initialize session state
if "processed_img" not in st.session_state:
    st.session_state.processed_img = None

uploaded_file = st.file_uploader("📤 Upload an image", type=ALLOWED_TYPES, help="Supported: PNG, JPG, JPEG, WEBP (Max 5MB)")

if uploaded_file:
    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("⚠️ File size exceeds 5MB limit. Please upload a smaller image.")
    else:
        # Optimize image loading
        img = Image.open(uploaded_file)
        
        # Convert to RGBA only if needed
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        # Resize large images for performance
        max_dimension = 2000
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            st.info(f"ℹ️ Image resized to {new_size[0]}x{new_size[1]} for optimal performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Original")
            st.image(img, use_container_width=True)
        
        if st.button("✨ Remove Background", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing..."):
                st.session_state.processed_img = remove(img)
            st.success("✅ Background removed!")
        
        if st.session_state.processed_img is not None:
            output = st.session_state.processed_img.copy()
            
            with st.sidebar:
                st.header("🎨 Edit Options")
                
                bg_option = st.radio("Background", ["Transparent", "Solid Color", "Custom Image"])
                
                if bg_option == "Solid Color":
                    bg_color = st.color_picker("Pick Color", "#FFFFFF")
                    bg = Image.new("RGBA", output.size, bg_color)
                    bg.paste(output, (0, 0), output)
                    output = bg
                
                elif bg_option == "Custom Image":
                    bg_file = st.file_uploader("Upload Background", type=ALLOWED_TYPES, key="bg")
                    if bg_file:
                        bg_img = Image.open(bg_file).convert("RGBA").resize(output.size, Image.Resampling.LANCZOS)
                        bg_img.paste(output, (0, 0), output)
                        output = bg_img
                
                st.divider()
                st.subheader("⚙️ Adjustments")
                
                brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
                contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
                sharpness = st.slider("Sharpness", 0.0, 2.0, 1.0, 0.1)
                
                # Apply adjustments only if changed
                if brightness != 1.0:
                    output = ImageEnhance.Brightness(output).enhance(brightness)
                if contrast != 1.0:
                    output = ImageEnhance.Contrast(output).enhance(contrast)
                if sharpness != 1.0:
                    output = ImageEnhance.Sharpness(output).enhance(sharpness)
                
                st.divider()
                blur = st.checkbox("Smooth Edges")
                if blur:
                    output = output.filter(ImageFilter.SMOOTH)
            
            with col2:
                st.subheader("✨ Result")
                st.image(output, use_container_width=True)
            
            st.divider()
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                buf_png = io.BytesIO()
                output.save(buf_png, format="PNG", optimize=True)
                st.download_button(
                    label="📥 Download PNG",
                    data=buf_png.getvalue(),
                    file_name="background_removed.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            with col_dl2:
                buf_jpg = io.BytesIO()
                output.convert("RGB").save(buf_jpg, format="JPEG", quality=95, optimize=True)
                st.download_button(
                    label="📥 Download JPEG",
                    data=buf_jpg.getvalue(),
                    file_name="background_removed.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
else:
    st.info("👆 Upload an image to get started")
    
    # Add instructions for better UX
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Upload** your image (PNG, JPG, JPEG, or WEBP)
        2. **Click** 'Remove Background' button
        3. **Customize** with editing options (optional)
        4. **Download** your edited image
        
        **Tips:**
        - Works best with clear subject and contrasting background
        - Maximum file size: 5MB
        - All processing happens securely - no data stored
        """)