# PRIVACY.md - Privacy Statement & Data Handling Policy

This application is built with **Privacy-by-Design** principles to protect user signature data.

---

## 1. What Data is Collected & Processed?

- **Received Data**: The application receives uploaded image files (or canvas drawing base64 data) containing handwritten signatures solely for real-time feature extraction and forgery classification.
- **Permanent Storage**: **ZERO SIGNATURE DATA IS PERMANENTLY STORED.**
- **Databases**: No databases (SQL, MongoDB, Firebase, PostgreSQL) are connected or used for storing signatures.
- **Third-Party APIs**: Signature images are **NEVER sent to external third parties** (no OpenAI, Gemini, AWS S3, Cloudinary, or analytics trackers).

---

## 2. Temporary Data Lifetime

1. The signature image enters server memory (RAM) via an encrypted HTTPS connection.
2. OpenCV and Scikit-Image preprocess the image and compute 9 mathematical features.
3. The Machine Learning model predicts the genuine/forged verdict.
4. The prediction result JSON is sent back to your browser.
5. **Memory Garbage Collection immediately releases the signature image array.**

---

## 3. Browser Storage & Logging

- Signatures are **NOT** stored in browser `localStorage` or `sessionStorage`.
- Object URLs created in JavaScript for image previews are revoked when no longer in use.
- Server logs contain **ONLY** operational status messages (e.g. `"Prediction completed successfully"`). No image bytes, pixel arrays, or filenames are logged.

---

## 4. Notice for Demonstration Use
> ⚠️ **Notice**: While this application does not permanently store uploaded signatures, users are advised to avoid uploading signatures from sensitive legal or financial documents on public web demonstrations.
