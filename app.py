"""
Bulk Image Compressor
=====================

A Flask web application for smart image compression.
Reduces image file sizes to approximately 500KB target
while maintaining visual quality.

Author: CreatorHub Team
Version: 1.0.0
License: MIT

Features:
- Smart compression targeting ~500KB file size
- Batch processing with progress tracking
- Drag and drop upload interface
- Quality preservation with iterative optimization
- Automatic format conversion (RGBA/P to RGB)
- Large image downscaling
- Bulk download support

Requirements:
- Python 3.8+
- Flask 3.0+
- Pillow (PIL)
- See requirements.txt for full dependencies

Usage:
    1. Install dependencies: pip install -r requirements.txt
    2. Run: python app.py
    3. Open: http://localhost:5000

API Endpoints:
    POST /api/compress           - Compress a single image
    GET  /api/download/<filename> - Download compressed image
    GET  /api/health             - Health check
"""

# =============================================================================
# IMPORTS
# =============================================================================

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
from datetime import datetime
import os
import io
import re
import tempfile

# =============================================================================
# CONFIGURATION
# =============================================================================

APP_NAME = "Bulk Image Compressor"
APP_VERSION = "1.0.0"
APP_AUTHOR = "CreatorHub Team"

TARGET_FILE_SIZE = 500 * 1024
MAX_DIMENSION = 2000
QUALITY_START = 85
QUALITY_MIN = 30
QUALITY_STEP = 5
MAX_UPLOAD_SIZE = 50 * 1024 * 1024

SUPPORTED_INPUT_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
UPLOAD_FOLDER = tempfile.mkdtemp()

# =============================================================================
# FLASK APPLICATION SETUP
# =============================================================================

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def sanitize_filename(filename):
    """Remove or replace special characters in filename."""
    name, ext = os.path.splitext(filename)
    safe_name = re.sub(r'[^\w\-_.]', '_', name)
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
    if not safe_name:
        safe_name = 'image'
    return f"{safe_name}{ext}"


def get_file_size(file):
    """Get file size in bytes."""
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size


def convert_to_rgb(image):
    """Convert image to RGB mode handling transparency."""
    if image.mode == 'RGB':
        return image
    if image.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        if image.mode in ('RGBA', 'LA'):
            if image.mode == 'LA':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1])
            return background
        return image.convert('RGB')
    return image.convert('RGB')


def downscale_if_needed(image, max_dim):
    """Downscale image if exceeds max dimension."""
    w, h = image.size
    if max(w, h) <= max_dim:
        return image
    if w > h:
        new_w, new_h = max_dim, int(h * (max_dim / w))
    else:
        new_h, new_w = max_dim, int(w * (max_dim / h))
    return image.resize((new_w, new_h), Image.Resampling.LANCZOS)


def compress_to_target(image, target, q_start, q_min, q_step):
    """Iteratively compress to target size."""
    quality = q_start
    output = io.BytesIO()
    while quality >= q_min:
        output.seek(0)
        output.truncate(0)
        image.save(output, format='JPEG', optimize=True, quality=quality)
        if output.tell() <= target:
            break
        quality -= q_step
    return output, quality


def compress_image(file):
    """Main compression pipeline."""
    try:
        original_size = get_file_size(file)
        original_filename = file.filename
        image = Image.open(file)
        
        name, ext = os.path.splitext(original_filename)
        new_filename = f"{name}1{ext}"
        safe_filename = sanitize_filename(new_filename)
        
        image = convert_to_rgb(image)
        image = downscale_if_needed(image, MAX_DIMENSION)
        output, final_quality = compress_to_target(image, TARGET_FILE_SIZE, QUALITY_START, QUALITY_MIN, QUALITY_STEP)
        
        temp_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        with open(temp_path, 'wb') as f:
            f.write(output.getvalue())
        
        new_size = output.tell()
        reduction = ((original_size - new_size) / original_size * 100) if original_size > 0 else 0
        
        return {
            'success': True,
            'original_name': original_filename,
            'new_name': new_filename,
            'safe_filename': safe_filename,
            'original_size': original_size,
            'new_size': new_size,
            'reduction': round(reduction, 2),
            'width': image.width,
            'height': image.height
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'original_name': file.filename if file else 'unknown'}


def log_compression(name, size, reduction, success):
    """Log compression operation."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "OK" if success else "FAIL"
    print(f"[{ts}] {status}: {name} -> {size/1024:.1f}KB ({reduction:.1f}%)")


# =============================================================================
# ROUTE HANDLERS
# =============================================================================

@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/compress', methods=['POST'])
def compress():
    """Compress uploaded image."""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        result = compress_image(file)
        
        if result.get('success'):
            log_compression(result['original_name'], result['new_size'], result['reduction'], True)
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download(filename):
    """Download compressed image."""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        
        safe_filename = sanitize_filename(filename)
        safe_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        if os.path.exists(safe_path):
            return send_file(safe_path, as_attachment=True, download_name=filename)
        
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'app_name': APP_NAME,
        'version': APP_VERSION,
        'target_size_kb': TARGET_FILE_SIZE // 1024,
        'max_dimension': MAX_DIMENSION,
        'upload_folder': UPLOAD_FOLDER
    })


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(f"  {APP_NAME}")
    print(f"  Version {APP_VERSION}")
    print("=" * 60)
    print(f"\n  Compression Settings:")
    print(f"    Target Size: {TARGET_FILE_SIZE // 1024} KB")
    print(f"    Max Dimension: {MAX_DIMENSION} px")
    print(f"    Quality Range: {QUALITY_MIN}-{QUALITY_START}")
    print(f"\n  Temp Folder: {UPLOAD_FOLDER}")
    print("\n  Open your browser and go to:")
    print("  http://localhost:5000")
    print("\n  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
