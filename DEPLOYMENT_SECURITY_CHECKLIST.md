# DEPLOYMENT_SECURITY_CHECKLIST.md

Use this checklist to verify that all privacy, security, and Render deployment requirements are fulfilled before launching publicly.

---

- [x] **HTTPS**: Production application runs over HTTPS on Render with automatic SSL certificates.
- [x] **Debug Disabled**: `FLASK_DEBUG=0` and `debug=False` enforced in production.
- [x] **No Hardcoded Secrets**: Secrets loaded via `os.environ.get('SECRET_KEY')`.
- [x] **`.env` Excluded from Git**: `.env` and `.env.local` included in `.gitignore`.
- [x] **Upload Size Limit**: `MAX_CONTENT_LENGTH = 5 * 1024 * 1024` (5 MB) enforced with HTTP 413 handling.
- [x] **MIME/Content Validation**: In-memory `Pillow` binary validation (`img.verify()`) restricting uploads to PNG, JPG, JPEG, BMP.
- [x] **Image Dimension Validation**: Bounded image dimensions (Max 4096×4096 px) to prevent decompression bombs.
- [x] **Path Traversal Protection**: Uploaded files processed directly in-memory; user filenames are never written to server disk paths.
- [x] **No Permanent Signature Storage**: Uploaded signature bytes are processed strictly in RAM and discarded immediately after inference.
- [x] **Temporary Files Deleted**: Zero disk files written during prediction pipeline.
- [x] **No Signature Logging**: Logging sanitized to contain operational status only (`"Prediction completed"`); no base64, image arrays, or signature bytes printed.
- [x] **No Signature in localStorage**: Frontend JavaScript stores zero signature data in `localStorage` or `sessionStorage`.
- [x] **No Signature in sessionStorage**: Verified clean client-side state.
- [x] **No Third-Party Image APIs**: ML inference performed 100% locally on Render instance; zero data sent to external AI/Cloud services.
- [x] **Safe Error Responses**: Internal tracebacks and file paths suppressed; user receives generic error messages.
- [x] **Security Headers**: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, and `Cache-Control: no-store` applied via middleware.
- [x] **CORS Restricted**: Same-origin requests default; no unrestricted `Access-Control-Allow-Origin: *`.
- [x] **Rate Limiting**: `Flask-Limiter` rate limits prediction endpoints to **15 requests/minute per IP**.
- [x] **Health Endpoint**: Endpoint `GET /health` implemented returning `{"status": "ok"}`.
- [x] **Production Server**: Configured `gunicorn app:app` production WSGI server in `Procfile`.
- [x] **Model Security**: Pre-trained model `models/signature_model.pkl` loaded once at startup; cannot be overwritten by user input.
- [x] **Render Environment Variables Configured**: `FLASK_ENV=production`, `SECRET_KEY`, `ENABLE_TRAINING_ENDPOINT=false` documented.
- [x] **Security Tests Pass**: Automated test suite (`python -m unittest discover -s tests`) passes 7/7 security tests cleanly.
