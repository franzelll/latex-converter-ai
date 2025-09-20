import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
import os
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globale Variablen für das Modell
tokenizer = None
model = None

def load_model(model_name: str = "microsoft/phi-4-mini-instruct"):
    """Lädt das Transformer-Modell für Text-Vereinfachung"""
    global tokenizer, model
    
    try:
        logger.info(f"Lade Modell: {model_name}")
        
        # Tokenizer laden
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Modell laden
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None
        )
        
        logger.info(f"Modell erfolgreich geladen auf {device}")
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim Laden des Modells: {e}")
        return False

def simplify_text(text: str, target_language: str = 'de') -> str:
    """Vereinfacht einzelnen Text"""
    if not tokenizer or not model:
        logger.warning("Modell nicht geladen, verwende Placeholder")
        return text
    
    try:
        prompt = (
            f"Vereinfache den folgenden Text in einfaches, verständliches {target_language}. "
            "Verwende kurze Sätze und einfache Wörter. Behalte alle wichtigen Informationen bei.\n\n"
            f"Text: {text}\n\n"
            f"Vereinfachter Text:"
        )
        
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        input_ids = inputs["input_ids"].to(model.device)
        attention_mask = inputs["attention_mask"].to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        simplified = decoded.split("Vereinfachter Text:")[-1].strip()
        
        return simplified if simplified else text
        
    except Exception as e:
        logger.error(f"Fehler bei der Text-Vereinfachung: {e}")
        return text

def simplify_text_batch(texts: List[str], target_language: str = 'de') -> List[str]:
    """Vereinfacht mehrere Texte gleichzeitig"""
    if not tokenizer or not model:
        logger.warning("Modell nicht geladen, verwende Placeholder")
        return texts
    
    try:
        prompts = []
        for text in texts:
            prompt = (
                f"Vereinfache den folgenden Text in einfaches {target_language}:\n\n"
                f"{text}\n\nVereinfachter Text:"
            )
            prompts.append(prompt)
        
        # Batch-Verarbeitung
        inputs = tokenizer(
            prompts, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=512
        )
        input_ids = inputs["input_ids"].to(model.device)
        attention_mask = inputs["attention_mask"].to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=128,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        simplified_texts = []
        
        for output in decoded:
            simplified = output.split("Vereinfachter Text:")[-1].strip()
            simplified_texts.append(simplified if simplified else "Text konnte nicht vereinfacht werden")
        
        return simplified_texts
        
    except Exception as e:
        logger.error(f"Fehler bei der Batch-Text-Vereinfachung: {e}")
        return texts

def simplify_full_text(text: str, target_language: str = 'de') -> str:
    """Vereinfacht längere Texte mit Chunking"""
    if not tokenizer or not model:
        logger.warning("Modell nicht geladen, verwende Placeholder")
        return text
    
    try:
        # Text in Chunks aufteilen für bessere Verarbeitung
        max_chunk_size = 500
        chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        if len(chunks) == 1:
            return simplify_text(text, target_language)
        
        # Chunks parallel verarbeiten
        simplified_chunks = simplify_text_batch(chunks, target_language)
        
        # Chunks wieder zusammenfügen
        return " ".join(simplified_chunks)
        
    except Exception as e:
        logger.error(f"Fehler bei der Volltext-Vereinfachung: {e}")
        return text

def initialize_model():
    """Initialisiert das Modell beim Start der Anwendung"""
    model_name = os.getenv('MODEL_NAME', 'microsoft/phi-4-mini-instruct')
    return load_model(model_name)

# Modell beim Import initialisieren
if __name__ != "__main__":
    initialize_model()
