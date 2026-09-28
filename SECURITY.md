# SECURITY.md - Security & Hardening Documentation

This document explains the security architecture, hardening controls, and risk mitigations implemented for the **Signature Forgery Detection Web Application**.

---

## 1. Security Architecture & Controls

### 🔒 In-Memory Processing (No Permanent Disk Storage)
- Uploaded signature files are processed strictly in RAM using `io.BytesIO` streams and NumPy pixel arrays.
- Files are **never written to disk** or temporary folders (`uploads/`, `temp/`, `.tmp/`).
- Zero signature data is logged or stored in any database.

### 🛡️ Strict File Upload Hardening
- **File Size Limit**: Configured `MAX_CONTENT_LENGTH = 5 * 1024 * 1024` (5 MB). Payloads exceeding 5MB are immediately rejected with HTTP 413.
- **MIME & Format Validation**: Files are checked via `Pillow` binary validation (`img.verify()`). Only `PNG`, `JPG`, `JPEG`, and `BMP` are accepted.
- **Decompression Bomb Protection**: Image dimensions are bounded (`10x10 px` minimum, `4096x4096 px` maximum).
- **Filename Handling**: User-provided filenames are completely ignored on the server to prevent Path Traversal attacks (`../../file`).

### ⚡ Rate Limiting & DoS Protection
- Powered by `Flask-Limiter` using IP-based tracking (`get_remote_address`).
- Endpoint `/api/predict` and `/api/verify_reference` are rate-limited to **15 requests per minute per IP**.
- Excessive requests return HTTP 429 Too Many Requests.

### 🔐 Security & Cache Headers
The application enforces strict HTTP security headers via Flask middleware:
- `X-Content-Type-Options: nosniff`: Prevents MIME-sniffing attacks.
- `X-Frame-Options: DENY`: Prevents Clickjacking attacks in iFrames.
- `Referrer-Policy: strict-origin-when-cross-origin`: Protects referrer information.
- `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`: Prevents browsers or proxies from caching signature images or prediction outputs.
- `Content-Security-Policy`: Binds script, style, image, and font sources tightly to prevent XSS.

### 🛑 Secret & Error Management
- Sensitive errors return generic user messages: `"Unable to process signature image. Please upload a valid signature file."`
- Internal tracebacks and file paths are hidden from HTTP responses.
- Application secrets are loaded via environment variables (`SECRET_KEY`).
- Debug mode (`debug=True`) is disabled by default in production.

---

## 2. Health Monitoring Endpoint
- Endpoint: `GET /health`
- Returns: `{"status": "ok", "model": "loaded"}` (HTTP 200) without exposing internal paths or system secrets.
