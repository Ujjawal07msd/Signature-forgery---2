# सही SIGNATURE — AI Signature Forgery Detection System

![Ujjawal Groups](https://img.shields.io/badge/Developed%20By-Ujjawal%20Groups-blue?style=for-the-badge)
![Website Audit](https://img.shields.io/badge/Audit%20Verified-Ujjawal%20Groups%20Website%20Audit-emerald?style=for-the-badge)
![Security](https://img.shields.io/badge/Privacy-Zero--Knowledge%20In--Memory-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/Backend-Python%20%7C%20Flask%20%7C%20OpenCV-blueviolet?style=for-the-badge)

**सही SIGNATURE** is an enterprise-grade AI-powered Biometric Signature Verification and Forgery Detection platform developed under **Ujjawal Groups** and verified by **Ujjawal Groups Website Audit**.

The system combines real-time **OpenCV Computer Vision pipelines**, **9 morphological & statistical feature extractors**, and a **dual Machine Learning architecture** (One-Class Anomaly Detection & Multi-Model Ensemble Classification) to detect genuine vs forged signatures with high accuracy.

---

## 🌟 Key Features & Capabilities

### 1. 🧠 Smart Verify Workbench (Targeted Verification)
- **Option 1: Quick Verify (Genuine Only)**
  - Requires **≥ 3 genuine reference signatures**.
  - Powered by **One-Class Anomaly Detection** using Euclidean distance, Cosine similarity, and Z-score dynamic thresholding.
- **Option 2: Full Training Mode (BEST Accuracy)**
  - Requires **≥ 3 genuine + ≥ 2 forged sample signatures**.
  - Trains an on-the-fly **Ensemble Classifier (Random Forest + Linear SVM + Centroid Distance Voting)** to learn exact genuine vs forgery characteristics.

### 2. ✏️ Smart Draw Canvas & Real-Time OpenCV Inspector
- **Interactive HTML5 Drawing Canvas**: Draw signatures directly on screen using mouse or touch.
- **Live Computer Vision Inspector**: Displays real-time grayscale and Otsu binarization feeds as strokes are drawn.
- **Drawn Reference Snapshots**: Collect multiple drawn genuine and forged reference signatures directly on canvas with 1-click thumbnail removal.

### 3. 🔬 Step-by-Step Preprocessing Pipeline Grid
Displays dynamic 4-stage transformation rows for **every** signature analyzed:
1. **Raw RGB Input**: Original uploaded or drawn image.
2. **Grayscale Reduction**: Single-channel intensity normalization.
3. **Otsu Adaptive Binarization**: Background ink noise removal.
4. **Bounding Crop**: Exact stroke contour bounding box isolation.

### 4. 📐 9 Morphological & Geometric Feature Metrics
Extracts structural signature footprints displayed in real-time via **Radar Footprint Charts** and detailed feature value tables:
1. **Aspect Ratio**: Ink area density per bounding box area.
2. **Normalized Vertical Mass Center ($Y$)**: Vertical center of ink gravity.
3. **Normalized Horizontal Mass Center ($X$)**: Horizontal center of ink gravity.
4. **Contour Eccentricity**: Shape elongation metric.
5. **Convex Solidity**: Ink area vs bounding convex hull ratio.
6. **Horizontal Slant Skewness ($X$)**: Stroke tilt along X-axis.
7. **Vertical Slant Skewness ($Y$)**: Stroke tilt along Y-axis.
8. **Horizontal Stroke Kurtosis ($X$)**: Peak stroke concentration & tremor noise.
9. **Vertical Stroke Kurtosis ($Y$)**: Peak vertical stroke concentration.

### 5. 🛡️ Zero-Knowledge Data Privacy & Security
- **100% In-Memory RAM Processing**: Images are parsed strictly in memory and **never saved to disk or database**.
- **Rate-Limited API**: Protected by `Flask-Limiter` against brute-force uploads.
- **Enterprise Security Headers**: Strict Content Security Policy (CSP), anti-clickjacking, and nosniff rules.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Flask, Scikit-Learn, OpenCV (`opencv-python-headless`), Scikit-Image, Pillow, NumPy, SciPy, Flask-Limiter.
- **Frontend**: Vanilla JavaScript (ES6+), Vanilla CSS (Custom Design System & Tokens), HTML5 Canvas API, Chart.js.
- **Deployment**: Production WSGI with Gunicorn (`Procfile`).

---

## 📁 Repository Structure

```
Signature-forgery/
├── app.py                      # Flask REST API server & Security Middleware
├── core/
│   ├── preprocessor.py         # OpenCV preprocessing pipeline & Base64 encoders
│   ├── feature_extractor.py    # 9 Morphological feature extractor engine
│   └── model.py                # Classifier model & Smart Verify algorithms
├── models/
│   └── signature_model.pkl     # Pre-trained enterprise model weights
├── static/
│   ├── css/
│   │   └── style.css           # Custom CSS design system
│   ├── js/
│   │   └── app.js              # Canvas, Smart Verify & Pipeline UI logic
│   ├── images/                 # Official brand logos & assets
│   └── video/                  # Ujjawal Groups Website Audit video
├── templates/
│   └── index.html              # Main application web interface
├── requirements.txt            # Python dependencies
├── Procfile                    # Production server entrypoint
└── README.md                   # Project documentation
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python **3.9+** or **3.10+**
- `pip` package manager

### 1. Clone the Repository
```bash
git clone https://github.com/Ujjawal07msd/Signature-forgery---2.git
cd Signature-forgery---2
```

### 2. Set Up Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000`.

---

## 🔌 API Reference

### 1. `POST /api/predict`
Single signature quick check against pre-trained enterprise dataset model.
- **Form Data**: `file` (Image) or `image_b64` (Base64 string)
- **Response**: JSON with `verdict`, `confidence`, `features`, `previews`.

### 2. `POST /api/smart_verify`
Smart verification comparing test signature against specific reference signatures.
- **Content-Type**: `multipart/form-data` or `application/json`
- **Payload**:
  - `mode`: `'genuine_only'` or `'full_training'`
  - `genuine_files` / `genuine_b64_list`: ≥ 3 genuine reference signatures
  - `forged_files` / `forged_b64_list`: ≥ 2 forged samples (in `full_training` mode)
  - `test_file` / `test_b64`: 1 unknown test signature
- **Response**: JSON with `verdict`, `confidence`, `method`, `method_details`, `features`, `previews`.

### 3. `GET /health`
System status check endpoint. Returns status `ok` and model load state.

---

## 👨‍💻 Developer & Brand Information

- **Brand**: Developed under **Ujjawal Groups**
- **Platform Verification**: **Ujjawal Groups Website Audit**
- **Email**: [ujjawal77.0077@gmail.com](mailto:ujjawal77.0077@gmail.com)
- **LinkedIn**: [Connect on LinkedIn](https://www.linkedin.com/in/ujjawalsharma0804/)

---

## 📜 Copyright & License

All Rights Reserved © 2026 **Ujjawal Groups**.  
Integrated with **Ujjawal Groups Website Audit Core**.
