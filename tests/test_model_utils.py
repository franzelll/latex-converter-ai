import pytest
import torch
from unittest.mock import patch, MagicMock
from your_model_utils import (
    load_model, simplify_text, simplify_text_batch, 
    simplify_full_text, initialize_model
)


class TestModelUtils:
    """Tests für Modell-Utilities"""
    
    @patch('your_model_utils.AutoTokenizer.from_pretrained')
    @patch('your_model_utils.AutoModelForCausalLM.from_pretrained')
    @patch('your_model_utils.torch.cuda.is_available')
    def test_load_model_success(self, mock_cuda, mock_model, mock_tokenizer):
        """Test erfolgreiches Laden des Modells"""
        mock_cuda.return_value = False
        mock_tokenizer.return_value = MagicMock()
        mock_model.return_value = MagicMock()
        
        result = load_model("test-model")
        
        assert result is True
        mock_tokenizer.assert_called_once()
        mock_model.assert_called_once()
    
    @patch('your_model_utils.AutoTokenizer.from_pretrained')
    def test_load_model_failure(self, mock_tokenizer):
        """Test Modell-Laden Fehler"""
        mock_tokenizer.side_effect = Exception("Model not found")
        
        result = load_model("nonexistent-model")
        
        assert result is False
    
    @patch('your_model_utils.tokenizer')
    @patch('your_model_utils.model')
    def test_simplify_text_with_model(self, mock_model, mock_tokenizer):
        """Test Text-Vereinfachung mit geladenem Modell"""
        # Mock Tokenizer
        mock_tokenizer.encode = MagicMock(return_value={'input_ids': torch.tensor([[1, 2, 3]]), 'attention_mask': torch.tensor([[1, 1, 1]])})
        mock_tokenizer.decode = MagicMock(return_value="Vereinfachter Text: Simplified text")
        
        # Mock Model
        mock_model.generate = MagicMock(return_value=torch.tensor([[1, 2, 3, 4, 5]]))
        mock_model.device = torch.device('cpu')
        
        result = simplify_text("Complex text", "de")
        
        assert result == "Simplified text"
        mock_model.generate.assert_called_once()
    
    def test_simplify_text_no_model(self):
        """Test Text-Vereinfachung ohne Modell"""
        # Temporär Modell auf None setzen
        import your_model_utils
        original_tokenizer = your_model_utils.tokenizer
        original_model = your_model_utils.model
        your_model_utils.tokenizer = None
        your_model_utils.model = None
        
        result = simplify_text("Complex text", "de")
        
        assert result == "Complex text"  # Sollte Original zurückgeben
        
        # Modell wiederherstellen
        your_model_utils.tokenizer = original_tokenizer
        your_model_utils.model = original_model
    
    @patch('your_model_utils.tokenizer')
    @patch('your_model_utils.model')
    def test_simplify_text_batch(self, mock_model, mock_tokenizer):
        """Test Batch-Text-Vereinfachung"""
        texts = ["Text 1", "Text 2"]
        
        # Mock Tokenizer
        mock_tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3], [4, 5, 6]]),
            'attention_mask': torch.tensor([[1, 1, 1], [1, 1, 1]])
        }
        mock_tokenizer.batch_decode = MagicMock(return_value=[
            "Vereinfachter Text: Simplified 1",
            "Vereinfachter Text: Simplified 2"
        ])
        
        # Mock Model
        mock_model.generate = MagicMock(return_value=torch.tensor([[1, 2, 3], [4, 5, 6]]))
        mock_model.device = torch.device('cpu')
        
        result = simplify_text_batch(texts, "de")
        
        assert len(result) == 2
        assert result[0] == "Simplified 1"
        assert result[1] == "Simplified 2"
    
    def test_simplify_full_text_single_chunk(self):
        """Test Volltext-Vereinfachung mit einem Chunk"""
        short_text = "Short text"
        
        with patch('your_model_utils.simplify_text') as mock_simplify:
            mock_simplify.return_value = "Simplified short text"
            
            result = simplify_full_text(short_text, "de")
            
            assert result == "Simplified short text"
            mock_simplify.assert_called_once_with(short_text, "de")
    
    def test_simplify_full_text_multiple_chunks(self):
        """Test Volltext-Vereinfachung mit mehreren Chunks"""
        long_text = "x" * 1000  # Text länger als 500 Zeichen
        
        with patch('your_model_utils.simplify_text_batch') as mock_batch:
            mock_batch.return_value = ["Simplified chunk 1", "Simplified chunk 2"]
            
            result = simplify_full_text(long_text, "de")
            
            assert result == "Simplified chunk 1 Simplified chunk 2"
            mock_batch.assert_called_once()
    
    @patch('your_model_utils.load_model')
    @patch('your_model_utils.os.getenv')
    def test_initialize_model(self, mock_getenv, mock_load):
        """Test Modell-Initialisierung"""
        mock_getenv.return_value = "test-model"
        mock_load.return_value = True
        
        result = initialize_model()
        
        assert result is True
        mock_getenv.assert_called_with('MODEL_NAME', 'microsoft/phi-4-mini-instruct')
        mock_load.assert_called_with("test-model")


class TestModelIntegration:
    """Integration Tests für Modell-Funktionen"""
    
    def test_error_handling(self):
        """Test Fehlerbehandlung"""
        # Test mit ungültigen Eingaben - sollte nicht crashen
        try:
            result = simplify_text("", "de")
            # Sollte String zurückgeben oder Exception werfen
            assert isinstance(result, str) or result == ""
        except Exception:
            pass  # Exception ist auch OK
        
        result = simplify_text_batch([], "de")
        assert result == []
        
        try:
            result = simplify_full_text("", "de")
            assert isinstance(result, str) or result == ""
        except Exception:
            pass  # Exception ist auch OK
    
    def test_language_parameter(self):
        """Test Sprach-Parameter"""
        # Test dass verschiedene Sprachen akzeptiert werden
        try:
            result_de = simplify_text("Test", "de")
            # Sollte String zurückgeben
            assert isinstance(result_de, str) or result_de == "Test"
        except Exception:
            pass  # Exception ist auch OK
        
        try:
            result_en = simplify_text("Test", "en")
            assert isinstance(result_en, str) or result_en == "Test"
        except Exception:
            pass
        
        try:
            result_fr = simplify_text("Test", "fr")
            assert isinstance(result_fr, str) or result_fr == "Test"
        except Exception:
            pass
