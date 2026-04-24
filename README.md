# 🖼️ Image Reducer

A Flask web application for smart image compression. Reduces image file sizes to ~500KB target while maintaining quality.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **Smart Compression**: Targets ~500KB file size
- **Quality Preservation**: Maintains visual quality with optimized JPEG compression
- **Batch Processing**: Compress multiple images at once
- **Drag & Drop**: Easy drag and drop interface
- **Progress Tracking**: Real-time compression progress
- **Bulk Download**: Download all compressed images at once

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/image-reducer.git
cd image-reducer
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open your browser and go to: **http://localhost:5000**

## 📝 How It Works

1. **Upload Images**: Drag & drop or click to select images
2. **Compress**: Click "Compress Images" button
3. **Download**: Download compressed images individually or all at once

### Compression Algorithm

1. Converts RGBA/P mode images to RGB
2. Downscales images larger than 2000px (maintains aspect ratio)
3. Iteratively reduces JPEG quality until target size (~500KB) is reached
4. Minimum quality floor of 30% to maintain usability

## 🗂️ Project Structure

```
image-reducer/
├── app.py              # Flask backend
├── templates/
│   └── index.html      # Frontend UI
├── static/             # Static files
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 📊 Supported Formats

| Format | Input | Output |
|--------|-------|--------|
| PNG | ✅ | JPEG |
| JPG/JPEG | ✅ | JPEG |
| WebP | ✅ | JPEG |
| TIFF | ✅ | JPEG |
| BMP | ✅ | JPEG |

## ⚙️ Configuration

You can modify these settings in `app.py`:

```python
# Target file size (default: 500KB)
target_size = 500 * 1024

# Maximum dimension (default: 2000px)
max_dimension = 2000

# Starting quality (default: 85)
quality = 85

# Quality step (default: 5)
step = 5

# Minimum quality (default: 30)
min_quality = 30
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
