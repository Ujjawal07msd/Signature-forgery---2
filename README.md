# Signature-forgery
Developed a signature verification system combining image processing and machine learning. The system extracts key features from scanned signature images — including centroid, eccentricity, solidity, skewness, and kurtosis — and uses a multi-layer neural network to classify signatures as "genuine or forged".

 Preprocessed signature images using grayscale conversion, noise filtering, and binary thresholding (Otsu’s method)
 Extracted 9 statistical and geometric features per image for training
 Created labeled datasets for 12 individuals and stored them in structured CSV format
 Built a feedforward neural network using TensorFlow (v1) with three hidden layers
 Achieved classification of unseen signatures with high accuracy using softmax predictions

Tools & Technologies:* Python, TensorFlow v1, NumPy, Pandas, Matplotlib, Scikit-image, Keras,
