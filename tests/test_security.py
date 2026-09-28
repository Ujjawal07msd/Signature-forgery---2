import os
import io
import unittest
import numpy as np
from PIL import Image
from app import app

class SecurityTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'ok')

    def test_02_valid_image_upload(self):
        """Test valid PNG image upload processed in-memory."""
        img = Image.new('RGB', (200, 100), color=(255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        response = self.client.post(
            '/api/predict',
            data={'file': (buf, 'valid_signature.png')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('verdict', data)
        self.assertIn('confidence', data)

    def test_03_invalid_fake_image(self):
        """Test text file renamed to .jpg is rejected."""
        fake_stream = io.BytesIO(b"This is malicious executable or plain text content.")
        response = self.client.post(
            '/api/predict',
            data={'file': (fake_stream, 'malicious.jpg')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_04_empty_upload(self):
        """Test empty upload is rejected."""
        response = self.client.post('/api/predict', data={})
        self.assertEqual(response.status_code, 400)

    def test_05_oversized_file(self):
        """Test file larger than 5 MB is rejected."""
        huge_bytes = b"0" * (6 * 1024 * 1024)  # 6 MB
        buf = io.BytesIO(huge_bytes)
        response = self.client.post(
            '/api/predict',
            data={'file': (buf, 'huge.png')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 413)

    def test_06_security_headers_present(self):
        """Test security headers are applied to HTTP responses."""
        response = self.client.get('/')
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('Cache-Control'), 'no-store, no-cache, must-revalidate, max-age=0')
        self.assertIn('Content-Security-Policy', response.headers)

    def test_07_no_disk_leak(self):
        """Verify that zero files are saved to uploads/ or temp/ directories."""
        self.assertFalse(os.path.exists('uploads') and len(os.listdir('uploads')) > 0)
        self.assertFalse(os.path.exists('temp') and len(os.listdir('temp')) > 0)

if __name__ == '__main__':
    unittest.main()
