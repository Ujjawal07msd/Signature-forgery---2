import os
import glob
import numpy as np
import pandas as pd
from PIL import Image

from core.preprocessor import preprocess_pipeline
from core.feature_extractor import extract_features
from core.model import SignatureClassifier
from create_sample_dataset import generate_dataset, GENUINE_DIR, FORGED_DIR, DATASET_DIR

FEATURES_CSV = os.path.join(os.path.dirname(__file__), 'signature_features.csv')

def load_and_extract_features():
    """
    Scans the dataset directory. Supports:
    1. Flat dataset/genuine/ and dataset/forged/ folders.
    2. CEDAR dataset subdirectories (e.g. signatures_1 to signatures_55, full_org, full_forg, original_*, forgeries_*).
    """
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR, exist_ok=True)
        
    all_files = glob.glob(os.path.join(DATASET_DIR, '**', '*.png'), recursive=True) + \
                glob.glob(os.path.join(DATASET_DIR, '**', '*.jpg'), recursive=True) + \
                glob.glob(os.path.join(DATASET_DIR, '**', '*.bmp'), recursive=True)
                
    if len(all_files) == 0:
        print("[!] No custom dataset found in dataset/. Generating synthetic sample dataset...")
        generate_dataset()
        all_files = glob.glob(os.path.join(DATASET_DIR, '**', '*.png'), recursive=True)

    records = []
    X = []
    y = []
    
    print(f"[+] Found {len(all_files)} total signature images in dataset directory.")
    
    for filepath in all_files:
        norm_path = filepath.lower().replace('\\', '/')
        fname = os.path.basename(norm_path)
        
        # Categorize Genuine (1) vs Forged (0) based on folder or filename
        if any(keyword in norm_path for keyword in ['genuine', 'original', 'full_org', 'org_']) or fname.startswith('original_'):
            label = 1
        elif any(keyword in norm_path for keyword in ['forged', 'forgery', 'forgeries', 'full_forg', 'forg_']) or fname.startswith('forgeries_'):
            label = 0
        else:
            # Default fallback if unknown
            continue
            
        try:
            img = np.array(Image.open(filepath))
            _, _, cropped = preprocess_pipeline(img)
            feat_dict, feat_vec = extract_features(cropped)
            feat_dict['label'] = label
            feat_dict['filename'] = os.path.basename(filepath)
            records.append(feat_dict)
            X.append(feat_vec)
            y.append(label)
        except Exception as e:
            print(f"[-] Warning: Error reading {filepath}: {e}")
            
    df = pd.DataFrame(records)
    df.to_csv(FEATURES_CSV, index=False)
    print(f"[+] Saved extracted feature dataset ({len(df)} records) to {FEATURES_CSV}")
    
    return np.array(X), np.array(y)

def main():
    print("="*60)
    print("      TRAINING SIGNATURE FORGERY DETECTION MODEL")
    print("="*60)
    
    X, y = load_and_extract_features()
    
    if len(X) == 0:
        print("[!] No valid genuine or forged images found. Check folder names!")
        return
        
    print(f"\n[+] Dataset Loaded successfully:")
    print(f"    - Genuine Signatures (Label 1): {np.sum(y == 1)}")
    print(f"    - Forged Signatures  (Label 0): {np.sum(y == 0)}")
    
    clf = SignatureClassifier(model_type='rf')
    accuracy = clf.train(X, y)
    
    print(f"\n[*] Model Training Accuracy: {accuracy * 100:.2f}%")
    clf.save()
    print("="*60)

if __name__ == '__main__':
    main()
