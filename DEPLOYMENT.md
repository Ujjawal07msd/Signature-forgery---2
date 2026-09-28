# DEPLOYMENT.md - Step-by-Step Render Deployment Guide

Follow these exact steps to deploy your hardened Signature Forgery Detection project securely on **Render**.

---

## 1. Prerequisites
- A free account on [Render.com](https://render.com).
- Your project pushed to a GitHub repository.

---

## 2. Environment Variables to Configure on Render

When setting up your Web Service on Render, add these Environment Variables in the **Environment** settings tab:

| Key | Value | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Enables production mode |
| `FLASK_DEBUG` | `0` | Disables debug mode and tracebacks |
| `SECRET_KEY` | *(Generate random strong string)* | Flask session/security secret |
| `ENABLE_TRAINING_ENDPOINT` | `false` | Disables public retraining endpoint |
| `PYTHON_VERSION` | `3.11.9` | Sets target Python version |

---

## 3. Exact Render Web Service Settings

- **Service Type**: Web Service
- **Environment**: Python 3
- **Region**: Select closest region (e.g. Oregon/Frankfurt/Singapore)
- **Branch**: `main`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  gunicorn app:app
  ```
- **Health Check Path**: `/health`
- **Instance Type**: Free (512 MB RAM)

---

## 4. Post-Deployment Verification

1. Open your live HTTPS link provided by Render (e.g. `https://signature-forgery-ai.onrender.com`).
2. Test `/health` endpoint: `https://signature-forgery-ai.onrender.com/health` $\rightarrow$ should return `{"status": "ok", "model": "loaded"}`.
3. Test uploading a sample signature image to verify predictions work smoothly.
