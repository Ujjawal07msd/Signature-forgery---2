import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import euclidean, cosine

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'signature_model.pkl')

class SignatureClassifier:
    def __init__(self, model_type: str = 'rf'):
        self.model_type = model_type
        if model_type == 'rf':
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            self.model = MLPClassifier(hidden_layer_sizes=(30, 20), max_iter=1000, random_state=42)
            
        self.scaler = StandardScaler()
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the classifier on extracted feature matrix X and labels y (1=Genuine, 0=Forged)."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        train_preds = self.model.predict(X_scaled)
        from sklearn.metrics import accuracy_score
        acc = accuracy_score(y, train_preds)
        return acc

    def predict(self, feature_vector: np.ndarray):
        """
        Predicts whether a signature is genuine or forged using trained model.
        
        Returns:
            is_genuine (bool): True if Genuine, False if Forged
            confidence (float): Probability score (0.0 to 100.0%)
        """
        if not self.is_trained:
            raise ValueError("Model is not trained yet. Train or load weights first.")
            
        if len(feature_vector.shape) == 1:
            feature_vector = feature_vector.reshape(1, -1)
            
        X_scaled = self.scaler.transform(feature_vector)
        pred = self.model.predict(X_scaled)[0]
        probs = self.model.predict_proba(X_scaled)[0]
        
        # Genuine probability (class 1)
        prob_genuine = probs[1] if len(probs) > 1 else (1.0 if pred == 1 else 0.0)
        confidence = float(prob_genuine * 100.0)
        is_genuine = bool(pred == 1)
        
        return is_genuine, confidence, probs.tolist()

    @staticmethod
    def compare_with_reference(ref_feature_vec: np.ndarray, test_feature_vec: np.ndarray, distance_threshold: float = 0.45):
        """
        Compares an unknown person's test signature against a reference genuine signature of that person.
        Calculates normalized Euclidean & Cosine feature distance.
        
        Returns:
            is_genuine (bool): True if similarity is high (distance <= threshold)
            similarity_pct (float): Match percentage score (0 to 100%)
            dist (float): Raw Euclidean feature distance
        """
        # Normalize vectors for fair distance calculation
        norm_ref = ref_feature_vec / (np.linalg.norm(ref_feature_vec) + 1e-6)
        norm_test = test_feature_vec / (np.linalg.norm(test_feature_vec) + 1e-6)
        
        dist = float(euclidean(norm_ref, norm_test))
        cos_sim = float(1.0 - cosine(norm_ref, norm_test))
        
        # Convert cosine similarity to 0-100% score
        similarity_pct = max(0.0, min(100.0, float(cos_sim * 100.0)))
        
        is_genuine = bool(dist <= distance_threshold)
        return is_genuine, round(similarity_pct, 2), round(dist, 4)

    @staticmethod
    def smart_verify_genuine_only(genuine_vectors: list, test_vector: np.ndarray, base_threshold: float = 0.35):
        """
        One-Class Anomaly Detection: Verifies test signature against a genuine profile
        built from 3+ reference genuine signatures. No forged samples needed.

        Algorithm:
        1. Compute mean/std of genuine feature vectors → genuine profile
        2. Compute z-scores, Euclidean distance, cosine similarity
        3. Dynamic threshold adapts to genuine sample consistency
        4. Combined score determines genuine vs forged
        """
        genuine_matrix = np.array(genuine_vectors)
        mean_genuine = np.mean(genuine_matrix, axis=0)
        std_genuine = np.std(genuine_matrix, axis=0)

        # Prevent division by zero
        std_genuine = np.where(std_genuine < 1e-6, 1e-6, std_genuine)

        # Z-score: how many std deviations is the test from genuine mean
        z_scores = np.abs(test_vector - mean_genuine) / std_genuine
        mean_z = float(np.mean(z_scores))

        # Normalized Euclidean distance
        norm_ref = mean_genuine / (np.linalg.norm(mean_genuine) + 1e-6)
        norm_test = test_vector / (np.linalg.norm(test_vector) + 1e-6)
        euc_dist = float(euclidean(norm_ref, norm_test))

        # Cosine similarity (1.0 = identical direction)
        cos_sim = float(1.0 - cosine(norm_ref, norm_test))

        # Dynamic threshold: consistent genuine → tighter threshold; variable → looser
        genuine_spread = float(np.mean(std_genuine / (np.abs(mean_genuine) + 1e-6)))
        dynamic_threshold = base_threshold * (1.0 + min(genuine_spread, 1.5))

        # Combined distance (weighted blend of all three metrics)
        combined_distance = 0.4 * euc_dist + 0.3 * (mean_z / 3.0) + 0.3 * (1.0 - cos_sim)

        is_genuine = bool(combined_distance <= dynamic_threshold)
        similarity_pct = max(0.0, min(100.0, (1.0 - combined_distance) * 100.0))

        return is_genuine, round(similarity_pct, 2), round(combined_distance, 4)

    @staticmethod
    def smart_verify_full_training(genuine_vectors: list, forged_vectors: list, test_vector: np.ndarray):
        """
        On-the-Fly Binary Classification: Trains RF + SVM + distance ensemble on genuine
        and forged samples, then predicts whether the test signature is genuine or forged.
        Best accuracy because it learns both classes.
        """
        from sklearn.svm import SVC
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.ensemble import RandomForestClassifier as RFC

        # Build training data
        X = np.array(list(genuine_vectors) + list(forged_vectors))
        y = np.array([1] * len(genuine_vectors) + [0] * len(forged_vectors))

        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        test_scaled = scaler.transform(test_vector.reshape(1, -1))

        # Model 1: Random Forest (robust with small samples)
        rf_clf = RFC(n_estimators=100, class_weight='balanced', random_state=42)
        rf_clf.fit(X_scaled, y)
        rf_pred = int(rf_clf.predict(test_scaled)[0])
        rf_probs = rf_clf.predict_proba(test_scaled)[0]
        rf_classes = list(rf_clf.classes_)
        rf_genuine_prob = float(rf_probs[rf_classes.index(1)]) if 1 in rf_classes else 0.0

        # Model 2: SVM with linear kernel (better for very small datasets)
        svm_clf = SVC(
            kernel='linear', probability=True, class_weight='balanced',
            C=0.5, random_state=42
        )
        svm_clf.fit(X_scaled, y)
        svm_pred = int(svm_clf.predict(test_scaled)[0])
        svm_probs = svm_clf.predict_proba(test_scaled)[0]
        svm_classes = list(svm_clf.classes_)
        svm_genuine_prob = float(svm_probs[svm_classes.index(1)]) if 1 in svm_classes else 0.0

        # Model 3: Distance-based (cosine similarity to genuine vs forged centroids)
        genuine_matrix = np.array(list(genuine_vectors))
        forged_matrix = np.array(list(forged_vectors))
        genuine_mean = np.mean(genuine_matrix, axis=0)
        forged_mean = np.mean(forged_matrix, axis=0)

        norm_g = genuine_mean / (np.linalg.norm(genuine_mean) + 1e-6)
        norm_f = forged_mean / (np.linalg.norm(forged_mean) + 1e-6)
        norm_t = test_vector / (np.linalg.norm(test_vector) + 1e-6)

        cos_sim_genuine = float(1.0 - cosine(norm_g, norm_t))
        cos_sim_forged = float(1.0 - cosine(norm_f, norm_t))
        dist_pred = 1 if cos_sim_genuine >= cos_sim_forged else 0

        # Majority vote ensemble (3 models)
        votes = [rf_pred, svm_pred, dist_pred]
        genuine_votes = sum(v == 1 for v in votes)
        is_genuine = genuine_votes >= 2  # majority rules

        # Confidence: weighted average of all model probabilities
        blended_prob = (0.4 * rf_genuine_prob + 0.35 * svm_genuine_prob + 0.25 * cos_sim_genuine)
        if is_genuine:
            confidence = float(blended_prob * 100.0)
        else:
            confidence = float((1.0 - blended_prob) * 100.0)

        confidence = max(0.0, min(100.0, confidence))

        method_details = {
            'rf_verdict': 'Genuine' if rf_pred == 1 else 'Forged',
            'svm_verdict': 'Genuine' if svm_pred == 1 else 'Forged',
            'distance_verdict': 'Genuine' if dist_pred == 1 else 'Forged',
            'models_agree': bool(genuine_votes == 3 or genuine_votes == 0),
            'rf_genuine_prob': round(rf_genuine_prob, 4),
            'svm_genuine_prob': round(svm_genuine_prob, 4),
            'cosine_sim_genuine': round(cos_sim_genuine, 4),
            'cosine_sim_forged': round(cos_sim_forged, 4)
        }

        return is_genuine, round(confidence, 2), method_details

    def save(self, filepath: str = MODEL_PATH):
        """Saves trained model and scaler to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'is_trained': self.is_trained
        }
        joblib.dump(data, filepath)
        print(f"[+] Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: str = MODEL_PATH):
        """Loads trained model and scaler from disk."""
        if not os.path.exists(filepath):
            return None
        data = joblib.load(filepath)
        clf = cls(model_type=data.get('model_type', 'rf'))
        clf.model = data['model']
        clf.scaler = data['scaler']
        clf.is_trained = data['is_trained']
        return clf

