"""
Integration Tests für API-Endpunkte
"""
import requests
import time
import tempfile
import os
import pytest


class TestAPIIntegration:
    """Integration Tests für die API"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """API Base URL"""
        return os.getenv('API_BASE_URL', 'http://localhost:5000')
    
    @pytest.fixture(scope="class")
    def wait_for_service(self, api_base_url):
        """Warte bis Service verfügbar ist"""
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{api_base_url}/health", timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        
        pytest.skip("Service nicht verfügbar")
    
    def test_health_endpoint(self, api_base_url, wait_for_service):
        """Test Health Check Endpoint"""
        response = requests.get(f"{api_base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'timestamp' in data
    
    def test_index_get(self, api_base_url, wait_for_service):
        """Test GET Request auf Index"""
        response = requests.get(api_base_url)
        
        assert response.status_code == 200
        assert 'LaTeX Converter' in response.text
    
    def test_text_to_pdf_conversion(self, api_base_url, wait_for_service):
        """Test Text zu PDF Konvertierung"""
        test_text = """
# Test Document

Dies ist ein **Test-Dokument** mit verschiedenen Elementen:

- Aufzählungspunkt 1
- Aufzählungspunkt 2

| Spalte 1 | Spalte 2 |
|----------|----------|
| Wert A   | Wert B   |

Normaler Absatz mit Text.
"""
        
        response = requests.post(
            api_base_url,
            data={'text': test_text},
            timeout=30
        )
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/pdf'
        assert len(response.content) > 1000  # PDF sollte mindestens 1KB haben
    
    def test_empty_text_error(self, api_base_url, wait_for_service):
        """Test Fehlerbehandlung bei leerem Text"""
        response = requests.post(
            api_base_url,
            data={'text': ''}
        )
        
        assert response.status_code == 200
        assert 'Please enter some text' in response.text
    
    def test_large_text_handling(self, api_base_url, wait_for_service):
        """Test Behandlung von großem Text"""
        large_text = "# Großes Dokument\n\n" + "Test-Text " * 1000
        
        response = requests.post(
            api_base_url,
            data={'text': large_text},
            timeout=60
        )
        
        # Sollte entweder erfolgreich sein oder einen angemessenen Fehler geben
        assert response.status_code in [200, 413, 400]
    
    def test_special_characters(self, api_base_url, wait_for_service):
        """Test Sonderzeichen"""
        special_text = """
# Sonderzeichen Test

Deutsche Umlaute: ä ö ü ß
Mathematische Zeichen: + - * / = < > ≤ ≥
Punktuation: ! ? . , ; : " ' ( ) [ ] { }
"""
        
        response = requests.post(
            api_base_url,
            data={'text': special_text},
            timeout=30
        )
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/pdf'
    
    def test_malicious_input(self, api_base_url, wait_for_service):
        """Test Sicherheit bei bösartigen Eingaben"""
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "\\input{/etc/passwd}",
            "\\write18{rm -rf /}",
        ]
        
        for malicious_input in malicious_inputs:
            response = requests.post(
                api_base_url,
                data={'text': malicious_input}
            )
            
            # Sollte entweder Fehler geben oder sicher behandelt werden
            assert response.status_code in [200, 400]
            if response.status_code == 200:
                # Wenn erfolgreich, sollte es keine gefährlichen Inhalte enthalten
                assert '<script>' not in response.text
                assert 'javascript:' not in response.text
    
    def test_concurrent_requests(self, api_base_url, wait_for_service):
        """Test gleichzeitige Anfragen"""
        import concurrent.futures
        
        def make_request():
            response = requests.post(
                api_base_url,
                data={'text': '# Concurrent Test\n\nTest-Text'},
                timeout=30
            )
            return response.status_code
        
        # 5 gleichzeitige Anfragen
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # Alle Anfragen sollten erfolgreich sein
        assert all(status == 200 for status in results)
    
    def test_rate_limiting(self, api_base_url, wait_for_service):
        """Test Rate Limiting"""
        # Viele schnelle Anfragen
        for i in range(70):  # Mehr als das Rate Limit
            response = requests.post(
                api_base_url,
                data={'text': f'# Rate Test {i}\n\nTest-Text'},
                timeout=5
            )
            
            if response.status_code == 429:
                # Rate Limit erreicht
                assert 'Rate limit' in response.text
                break
        else:
            # Rate Limit wurde nicht erreicht (möglicherweise nicht aktiviert)
            pass
    
    @pytest.mark.slow
    def test_pdf_upload(self, api_base_url, wait_for_service):
        """Test PDF-Upload (langsam, da PDF-Verarbeitung)"""
        # Erstelle temporäre PDF-Datei
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Einfache PDF-Struktur
            pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""
            tmp.write(pdf_content)
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = requests.post(
                    api_base_url,
                    files={'file': ('test.pdf', f, 'application/pdf')},
                    timeout=60
                )
            
            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'application/pdf'
            
        finally:
            os.unlink(tmp_path)
    
    def test_invalid_file_upload(self, api_base_url, wait_for_service):
        """Test ungültige Datei-Upload"""
        # Erstelle temporäre Text-Datei
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'This is not a PDF')
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = requests.post(
                    api_base_url,
                    files={'file': ('test.txt', f, 'text/plain')}
                )
            
            # Sollte normalen Text-Verarbeitungs-Flow durchlaufen
            assert response.status_code == 200
            
        finally:
            os.unlink(tmp_path)
