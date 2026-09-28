import numpy as np
from skimage.measure import regionprops

def compute_ratio(cropped_img: np.ndarray) -> float:
    """Feature 1: Aspect Ratio (Ink Pixel Count / Total Area)"""
    ink_pixels = np.sum(cropped_img == True)
    total_pixels = cropped_img.shape[0] * cropped_img.shape[1]
    if total_pixels == 0:
        return 0.0
    return float(ink_pixels / total_pixels)

def compute_centroid(cropped_img: np.ndarray):
    """Features 2 & 3: Normalized Centroid (Y, X)"""
    r, c = np.where(cropped_img == True)
    if len(r) == 0:
        return 0.5, 0.5
    cent_y = np.mean(r) / cropped_img.shape[0]
    cent_x = np.mean(c) / cropped_img.shape[1]
    return float(cent_y), float(cent_x)

def compute_eccentricity_solidity(cropped_img: np.ndarray):
    """Features 4 & 5: Eccentricity and Solidity using skimage regionprops"""
    props = regionprops(cropped_img.astype(np.int8))
    if len(props) == 0:
        return 0.0, 0.0
    return float(props[0].eccentricity), float(props[0].solidity)

def compute_skew_kurtosis(cropped_img: np.ndarray):
    """
    Features 6, 7, 8, 9: Skewness (X, Y) and Kurtosis (X, Y)
    Measures slant asymmetry and stroke density peak sharpness.
    """
    h, w = cropped_img.shape
    if h <= 1 or w <= 1 or np.sum(cropped_img) == 0:
        return (0.0, 0.0), (0.0, 0.0)
        
    x = np.arange(w)
    y = np.arange(h)
    
    xp = np.sum(cropped_img, axis=0)  # Projections along X
    yp = np.sum(cropped_img, axis=1)  # Projections along Y
    
    total_ink = np.sum(cropped_img)
    if total_ink == 0:
        return (0.0, 0.0), (0.0, 0.0)
        
    # Centroids along X and Y
    cx = np.sum(x * xp) / np.sum(xp) if np.sum(xp) > 0 else w / 2.0
    cy = np.sum(y * yp) / np.sum(yp) if np.sum(yp) > 0 else h / 2.0
    
    # Standard deviations
    sx = np.sqrt(np.sum(((x - cx) ** 2) * xp) / total_ink)
    sy = np.sqrt(np.sum(((y - cy) ** 2) * yp) / total_ink)
    
    sx = max(sx, 1e-5)
    sy = max(sy, 1e-5)
    
    # Skewness
    skew_x = np.sum(xp * ((x - cx) ** 3)) / (total_ink * (sx ** 3))
    skew_y = np.sum(yp * ((y - cy) ** 3)) / (total_ink * (sy ** 3))
    
    # Kurtosis (excess kurtosis relative to normal distribution)
    kurt_x = (np.sum(xp * ((x - cx) ** 4)) / (total_ink * (sx ** 4))) - 3.0
    kurt_y = (np.sum(yp * ((y - cy) ** 4)) / (total_ink * (sy ** 4))) - 3.0
    
    return (float(skew_x), float(skew_y)), (float(kurt_x), float(kurt_y))

def extract_features(cropped_img: np.ndarray) -> dict:
    """
    Extracts all 9 signature features from cropped binary signature image.
    
    Returns dictionary with feature names & values, and feature vector array.
    """
    ratio = compute_ratio(cropped_img)
    cent_y, cent_x = compute_centroid(cropped_img)
    eccentricity, solidity = compute_eccentricity_solidity(cropped_img)
    (skew_x, skew_y), (kurt_x, kurt_y) = compute_skew_kurtosis(cropped_img)
    
    feature_dict = {
        'ratio': ratio,
        'cent_y': cent_y,
        'cent_x': cent_x,
        'eccentricity': eccentricity,
        'solidity': solidity,
        'skew_x': skew_x,
        'skew_y': skew_y,
        'kurt_x': kurt_x,
        'kurt_y': kurt_y
    }
    
    feature_vector = np.array([
        ratio, cent_y, cent_x, eccentricity, solidity,
        skew_x, skew_y, kurt_x, kurt_y
    ], dtype=np.float32)
    
    return feature_dict, feature_vector
