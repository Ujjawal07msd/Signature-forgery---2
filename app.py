import os
import io
import base64
import logging
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.preprocessor import preprocess_pipeline, array_to_base64
from core.feature_extractor import extract_features
from core.model import SignatureClassifier, MODEL_PATH

# Configure safe operational logging (NO signature data/bytes logged)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security Config
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB upload limit
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Rate Limiter setup
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Load trained ML Model once at startup
classifier = SignatureClassifier.load(MODEL_PATH)
if classifier is None:
    logger.warning("Pre-trained model weights not found at startup.")
else:
    logger.info("Pre-trained Signature Classifier loaded successfully.")

# Allowed MIME / Image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_IMAGE_DIMENSION = 4096  # Max 4096 x 4096 px to prevent decompression bombs
MIN_IMAGE_DIMENSION = 10    # Min 10 x 10 px

def validate_and_load_image(raw_bytes: bytes) -> np.ndarray:
    """
    Validates image in-memory: checks file integrity, MIME format, and size dimensions.
    Returns RGB numpy array without saving any files to disk.
    """
    if not raw_bytes or len(raw_bytes) == 0:
        raise ValueError("Empty image file provided.")

    stream = io.BytesIO(raw_bytes)
    
    # 1. Verify Pillow can parse image
    try:
        with Image.open(stream) as img:
            img_format = img.format.lower() if img.format else ''
            if img_format not in ALLOWED_EXTENSIONS:
                raise ValueError(f"Unsupported image format: '{img_format}'. Allowed formats: PNG, JPG, JPEG, BMP.")
            
            # Verify file integrity
            img.verify()
            
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError("Invalid or corrupted image file.")

    # 2. Re-open stream to load pixel data and check dimensions
    stream.seek(0)
    with Image.open(stream) as img:
        img_rgb = img.convert('RGB')
        width, height = img_rgb.size
        
        if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
            raise ValueError(f"Image dimensions ({width}x{height}) exceed maximum allowed limit ({MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}).")
        if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
            raise ValueError(f"Image dimensions ({width}x{height}) are too small.")
            
        return np.array(img_rgb)

# Security Headers Middleware
@app.after_request
def apply_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    return response

@app.errorhandler(413)
def request_entity_too_large(error):
    logger.warning("Rejected upload exceeding size limit.")
    return jsonify({'error': 'File size exceeds maximum limit of 5 MB.'}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning("Rate limit exceeded for IP.")
    return jsonify({'error': 'Rate limit exceeded. Please wait a moment before trying again.'}), 429

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Render deployment monitoring."""
    model_status = 'loaded' if (classifier and classifier.is_trained) else 'not_loaded'
    return jsonify({'status': 'ok', 'model': model_status}), 200

@app.route('/api/predict', methods=['POST'])
@limiter.limit("15 per minute")
def predict():
    logger.info("Prediction request received.")
    try:
        if request.content_length and request.content_length > app.config['MAX_CONTENT_LENGTH']:
            logger.warning("Rejected upload exceeding size limit.")
            return jsonify({'error': 'File size exceeds maximum limit of 5 MB.'}), 413

        data = request.get_json(silent=True) if request.is_json else request.form
        raw_bytes = None

        # Option 1: Base64 canvas string
        if 'image_b64' in data and data['image_b64']:
            b64_data = data['image_b64']
            if ',' in b64_data:
                b64_data = b64_data.split(',')[1]
            raw_bytes = base64.b64decode(b64_data)
            
        # Option 2: Multipart File Upload
        elif 'file' in request.files:
            file = request.files['file']
            raw_bytes = file.read()
            
        if not raw_bytes:
            return jsonify({'error': 'No signature image provided.'}), 400

        # Validate image in-memory
        img = validate_and_load_image(raw_bytes)

        # In-Memory OpenCV & Preprocessing Pipeline
        gray, binary, cropped = preprocess_pipeline(img)
        
        # Previews for UI
        original_b64 = array_to_base64(img)
        gray_b64 = array_to_base64(gray)
        binary_b64 = array_to_base64(binary, is_bool=True)
        cropped_b64 = array_to_base64(cropped, is_bool=True)
        
        # Extract features
        feat_dict, feat_vec = extract_features(cropped)
        
        # Predict using in-memory model
        global classifier
        if classifier is None or not classifier.is_trained:
            classifier = SignatureClassifier.load(MODEL_PATH)
            
        if classifier is None or not classifier.is_trained:
            return jsonify({'error': 'Signature classifier model is unavailable.'}), 500

        is_genuine, confidence, probabilities = classifier.predict(feat_vec)
        logger.info("Prediction completed successfully.")
        
        return jsonify({
            'success': True,
            'verdict': 'Genuine' if is_genuine else 'Forged',
            'is_genuine': is_genuine,
            'confidence': round(confidence, 2),
            'features': feat_dict,
            'previews': {
                'original': original_b64,
                'grayscale': gray_b64,
                'binary': binary_b64,
                'cropped': cropped_b64
            }
        })
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception:
        logger.error("An unexpected error occurred during prediction.")
        return jsonify({'error': 'Unable to process signature image. Please upload a valid signature file.'}), 500

@app.route('/api/verify_reference', methods=['POST'])
@limiter.limit("15 per minute")
def verify_reference():
    logger.info("Reference comparison request received.")
    try:
        ref_file = request.files.get('reference_file')
        test_file = request.files.get('test_file')
        
        if not ref_file or not test_file:
            return jsonify({'error': 'Please provide both reference and test signature images.'}), 400
            
        ref_bytes = ref_file.read()
        test_bytes = test_file.read()
        
        ref_img = validate_and_load_image(ref_bytes)
        test_img = validate_and_load_image(test_bytes)
        
        _, _, ref_cropped = preprocess_pipeline(ref_img)
        _, _, test_cropped = preprocess_pipeline(test_img)
        
        _, ref_vec = extract_features(ref_cropped)
        test_feat_dict, test_vec = extract_features(test_cropped)
        
        is_genuine, similarity_pct, dist = SignatureClassifier.compare_with_reference(ref_vec, test_vec)
        logger.info("Reference comparison completed successfully.")
        
        return jsonify({
            'success': True,
            'verdict': 'Genuine' if is_genuine else 'Forged',
            'is_genuine': is_genuine,
            'confidence': similarity_pct,
            'distance': dist,
            'features': test_feat_dict,
            'previews': {
                'original': array_to_base64(test_img),
                'grayscale': array_to_base64(preprocess_pipeline(test_img)[0]),
                'binary': array_to_base64(preprocess_pipeline(test_img)[1], is_bool=True),
                'cropped': array_to_base64(test_cropped, is_bool=True)
            }
        })
    except ValueError as ve:
        logger.warning(f"Validation error in reference comparison: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception:
        logger.error("An unexpected error occurred during reference comparison.")
        return jsonify({'error': 'Unable to process signature images. Please check the uploaded files.'}), 500

@app.route('/api/smart_verify', methods=['POST'])
@limiter.limit("10 per minute")
def smart_verify():
    """Smart Verify: Supports both multipart file uploads and base64 drawn signatures."""
    logger.info("Smart verify request received.")
    try:
        if request.is_json:
            data = request.get_json(silent=True) or {}
            mode = data.get('mode', 'genuine_only')
            
            def parse_b64(b64_str):
                if not b64_str:
                    return None
                if ',' in b64_str:
                    b64_str = b64_str.split(',')[1]
                return base64.b64decode(b64_str)

            genuine_raw_list = [parse_b64(b) for b in data.get('genuine_b64_list', []) if b]
            forged_raw_list = [parse_b64(b) for b in data.get('forged_b64_list', []) if b]
            test_raw = parse_b64(data.get('test_b64'))
        else:
            mode = request.form.get('mode', 'genuine_only')
            genuine_files = request.files.getlist('genuine_files')
            forged_files = request.files.getlist('forged_files')
            test_file = request.files.get('test_file')

            genuine_raw_list = [f.read() for f in genuine_files if f]
            forged_raw_list = [f.read() for f in forged_files if f]
            test_raw = test_file.read() if test_file else None

        if mode not in ('genuine_only', 'full_training'):
            return jsonify({'error': 'Invalid mode. Use "genuine_only" or "full_training".'}), 400

        if not genuine_raw_list or len(genuine_raw_list) < 3:
            count = len(genuine_raw_list) if genuine_raw_list else 0
            return jsonify({'error': f'Please provide at least 3 genuine reference signatures. You provided {count}.'}), 400

        if not test_raw:
            return jsonify({'error': 'Please provide 1 test signature to verify.'}), 400

        if mode == 'full_training' and (not forged_raw_list or len(forged_raw_list) < 2):
            count = len(forged_raw_list) if forged_raw_list else 0
            return jsonify({'error': f'Full Training mode requires at least 2 forged samples. You provided {count}.'}), 400

        # Process genuine images
        genuine_vectors = []
        genuine_previews = []
        for raw in genuine_raw_list:
            img = validate_and_load_image(raw)
            gray, binary, cropped = preprocess_pipeline(img)
            _, feat_vec = extract_features(cropped)
            genuine_vectors.append(feat_vec)
            genuine_previews.append({
                'original': array_to_base64(img),
                'grayscale': array_to_base64(gray),
                'binary': array_to_base64(binary, is_bool=True),
                'cropped': array_to_base64(cropped, is_bool=True)
            })

        # Process forged images (only in full_training mode)
        forged_vectors = []
        forged_previews = []
        if mode == 'full_training':
            for raw in forged_raw_list:
                img = validate_and_load_image(raw)
                gray, binary, cropped = preprocess_pipeline(img)
                _, feat_vec = extract_features(cropped)
                forged_vectors.append(feat_vec)
                forged_previews.append({
                    'original': array_to_base64(img),
                    'grayscale': array_to_base64(gray),
                    'binary': array_to_base64(binary, is_bool=True),
                    'cropped': array_to_base64(cropped, is_bool=True)
                })

        # Process test image
        test_img = validate_and_load_image(test_raw)
        test_gray, test_binary, test_cropped = preprocess_pipeline(test_img)
        test_feat_dict, test_feat_vec = extract_features(test_cropped)
        test_preview = {
            'original': array_to_base64(test_img),
            'grayscale': array_to_base64(test_gray),
            'binary': array_to_base64(test_binary, is_bool=True),
            'cropped': array_to_base64(test_cropped, is_bool=True)
        }

        # Run appropriate ML algorithm
        if mode == 'full_training':
            is_genuine, confidence, method_details = SignatureClassifier.smart_verify_full_training(
                genuine_vectors, forged_vectors, test_feat_vec
            )
            method_name = 'SVM + 1-NN Ensemble (Full Training)'
        else:
            is_genuine, confidence, distance = SignatureClassifier.smart_verify_genuine_only(
                genuine_vectors, test_feat_vec
            )
            method_name = 'One-Class Anomaly Detection (Genuine Only)'
            method_details = {'distance': distance}

        logger.info(f"Smart verify completed. Mode: {mode}, Verdict: {'Genuine' if is_genuine else 'Forged'}")

        return jsonify({
            'success': True,
            'mode': mode,
            'verdict': 'Genuine' if is_genuine else 'Forged',
            'is_genuine': is_genuine,
            'confidence': confidence,
            'method': method_name,
            'method_details': method_details,
            'features': test_feat_dict,
            'previews': {
                'genuine': genuine_previews,
                'forged': forged_previews,
                'test': test_preview
            }
        })
    except ValueError as ve:
        logger.warning(f"Validation error in smart verify: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in smart verify: {e}")
        return jsonify({'error': 'Unable to process signatures. Please check your inputs and try again.'}), 500

@app.route('/api/train', methods=['POST'])
def train():
    # Retraining disabled in public production unless explicitly enabled via environment variable
    if os.environ.get('ENABLE_TRAINING_ENDPOINT', 'false').lower() != 'true':
        return jsonify({'error': 'Retraining endpoint is disabled in production environment.'}), 403

    try:
        from train_model import main as train_main
        train_main()
        global classifier
        classifier = SignatureClassifier.load(MODEL_PATH)
        return jsonify({'success': True, 'message': 'Model re-trained successfully!'})
    except Exception:
        logger.error("Error during retraining.")
        return jsonify({'error': 'Training failed.'}), 500

if __name__ == '__main__':
    is_debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=5000, debug=is_debug)
