import numpy as np
import cv2
from scipy import ndimage
from skimage.filters import threshold_otsu
import base64

def rgb_to_gray(img: np.ndarray) -> np.ndarray:
    """Converts RGB/RGBA image array to Grayscale (2D float array 0-255)."""
    if len(img.shape) == 3:
        if img.shape[2] == 4:  # RGBA
            # Convert RGBA to RGB using white background
            alpha = img[:, :, 3] / 255.0
            gray = (0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]) * alpha + 255.0 * (1.0 - alpha)
            return gray.astype(np.float32)
        elif img.shape[2] == 3:  # RGB
            gray = 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
            return gray.astype(np.float32)
    return img.astype(np.float32)

def gray_to_binary(gray_img: np.ndarray, blur_radius: float = 0.8) -> np.ndarray:
    """
    Applies Gaussian filter for noise reduction and Otsu thresholding
    to convert grayscale image to binary boolean array (True for signature ink, False for background).
    """
    # Smooth small background noise
    smoothed = ndimage.gaussian_filter(gray_img, blur_radius)
    
    # Calculate Otsu threshold
    try:
        thres = threshold_otsu(smoothed)
    except Exception:
        thres = np.mean(smoothed)
        
    # Pixels darker than threshold are signature ink (True)
    binary = smoothed < thres
    return binary

def crop_signature(binary_img: np.ndarray) -> np.ndarray:
    """
    Crops the binary image tightly to the bounding box surrounding the signature ink.
    """
    r, c = np.where(binary_img == True)
    if len(r) == 0 or len(c) == 0:
        # Fallback if blank image
        return binary_img
    
    r_min, r_max = r.min(), r.max()
    c_min, c_max = c.min(), c.max()
    
    cropped = binary_img[r_min:r_max + 1, c_min:c_max + 1]
    return cropped

def preprocess_pipeline(img: np.ndarray):
    """
    Runs full preprocessing pipeline and returns intermediate steps.
    
    Returns:
        gray: 2D float grayscale array
        binary: 2D bool binary array
        cropped: 2D bool cropped signature array
    """
    gray = rgb_to_gray(img)
    binary = gray_to_binary(gray)
    cropped = crop_signature(binary)
    return gray, binary, cropped

def array_to_base64(img_array: np.ndarray, is_bool: bool = False) -> str:
    """Helper to convert numpy array image into base64 PNG string for Web UI preview."""
    if is_bool:
        # Convert bool (True=ink) to 0=black ink on 255=white background
        display_img = np.where(img_array, 0, 255).astype(np.uint8)
    else:
        display_img = np.clip(img_array, 0, 255).astype(np.uint8)
        
    _, buffer = cv2.imencode('.png', display_img)
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"
