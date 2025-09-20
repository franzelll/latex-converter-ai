import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from app import app, create_layout_preserving_simplified_pdf


class TestFlaskApp:
    """Tests für Flask-Anwendung"""
    
    @pytest.fixture
    def client(self):
        """Test-Client erstellen"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_index_get(self, client):
        """Test GET-Request auf Index"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'LaTeX Converter' in response.data
    
    def test_index_post_empty_text(self, client):
        """Test POST mit leerem Text"""
        response = client.post('/', data={'text': ''})
        assert response.status_code == 200
        assert b'Please enter some text' in response.data
    
    @patch('app.LatexConverter')
    @patch('app.create_layout_preserving_simplified_pdf')
    def test_index_post_success(self, mock_pdf, mock_converter_class, client):
        """Test erfolgreicher POST-Request"""
        # Mock LatexConverter
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter
        mock_converter.process_text.return_value = None
        
        # Mock PDF-Erstellung
        mock_pdf.return_value = None
        
        response = client.post('/', data={'text': 'Test text'})
        
        # Sollte PDF-Download sein
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/pdf'
    
    @patch('app.LatexConverter')
    def test_index_post_processing_error(self, mock_converter_class, client):
        """Test POST mit Verarbeitungsfehler"""
        # Mock LatexConverter mit Fehler
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter
        mock_converter.process_text.side_effect = Exception("Processing error")
        
        response = client.post('/', data={'text': 'Test text'})
        
        assert response.status_code == 200
        assert b'Error processing text' in response.data
    
    @patch('app.fitz.open')
    def test_pdf_upload_success(self, mock_fitz, client):
        """Test erfolgreicher PDF-Upload"""
        # Mock PDF-Dokument
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_page = MagicMock()
        mock_page.get_text.return_value = {"blocks": []}
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.return_value = mock_doc
        
        # Mock vereinfachte PDF-Erstellung
        with patch('app.simplify_full_text') as mock_simplify:
            mock_simplify.return_value = "Simplified text"
            
            # Erstelle temporäre PDF-Datei
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(b'%PDF-1.4 fake pdf content')
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, 'rb') as f:
                    response = client.post('/', data={'file': (f, 'test.pdf')})
                
                assert response.status_code == 200
                assert response.headers['Content-Type'] == 'application/pdf'
            finally:
                os.unlink(tmp_path)
    
    def test_pdf_upload_wrong_format(self, client):
        """Test PDF-Upload mit falschem Format"""
        # Erstelle temporäre Text-Datei
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'This is not a PDF')
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = client.post('/', data={'file': (f, 'test.txt')})
            
            # Sollte normalen Text-Verarbeitungs-Flow durchlaufen
            assert response.status_code == 200
        finally:
            os.unlink(tmp_path)


class TestPDFProcessing:
    """Tests für PDF-Verarbeitung"""
    
    @patch('app.fitz.open')
    @patch('app.simplify_full_text')
    def test_create_layout_preserving_simplified_pdf(self, mock_simplify, mock_fitz):
        """Test PDF-Layout-erhaltende Vereinfachung"""
        # Mock PDF-Dokument
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        
        mock_page = MagicMock()
        mock_page.rect.width = 595
        mock_page.rect.height = 842
        mock_page.get_text.return_value = {
            "blocks": [{
                "lines": [{
                    "spans": [{"text": "Original text"}]
                }]
            }]
        }
        
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.return_value = mock_doc
        
        # Mock vereinfachter Text
        mock_simplify.return_value = "Simplified text"
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_pdf:
            input_pdf.write(b'%PDF-1.4 fake pdf')
            input_pdf_path = input_pdf.name
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_pdf:
            output_pdf_path = output_pdf.name
        
        try:
            create_layout_preserving_simplified_pdf(input_pdf_path, output_pdf_path)
            
            # Überprüfe, dass Funktionen aufgerufen wurden
            mock_fitz.assert_called()
            mock_simplify.assert_called_once()
            
        finally:
            os.unlink(input_pdf_path)
            os.unlink(output_pdf_path)
    
    @patch('app.fitz.open')
    def test_create_layout_preserving_simplified_pdf_error(self, mock_fitz):
        """Test PDF-Verarbeitung mit Fehler"""
        mock_fitz.side_effect = Exception("PDF processing error")
        
        with pytest.raises(Exception):
            create_layout_preserving_simplified_pdf("input.pdf", "output.pdf")


class TestErrorHandling:
    """Tests für Fehlerbehandlung"""
    
    @pytest.fixture
    def client(self):
        """Test-Client erstellen"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_unhandled_exception(self, client):
        """Test unbehandelte Ausnahmen"""
        with patch('app.LatexConverter') as mock_converter_class:
            mock_converter_class.side_effect = Exception("Unexpected error")
            
            response = client.post('/', data={'text': 'Test text'})
            
            assert response.status_code == 200
            assert b'Error:' in response.data
            assert b'Traceback:' in response.data


class TestConfiguration:
    """Tests für Konfiguration"""
    
    def test_app_config(self):
        """Test App-Konfiguration"""
        assert app.secret_key is not None
        assert app.secret_key != 'your-secret-key-here'  # Sollte geändert werden
    
    def test_environment_variables(self):
        """Test Umgebungsvariablen"""
        # PATH sollte LaTeX-Compiler enthalten
        path = os.environ.get('PATH', '')
        assert '/Library/TeX/texbin:' in path or 'latex' in path.lower()
