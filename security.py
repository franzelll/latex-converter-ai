"""
Security utilities für LaTeX Converter
"""
import os
import re
import hashlib
import secrets
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Zentrale Sicherheitsverwaltung"""
    
    def __init__(self, app=None):
        self.app = app
        self.allowed_extensions = {'pdf', 'txt', 'md'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.rate_limit_storage = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialisiere Sicherheitskonfiguration"""
        app.config.setdefault('MAX_CONTENT_LENGTH', self.max_file_size)
        app.config.setdefault('SECRET_KEY', self.generate_secret_key())
        
        # Rate Limiting Decorator registrieren
        app.before_request(self.check_rate_limit)
    
    def generate_secret_key(self):
        """Generiere sicheren Secret Key"""
        return secrets.token_urlsafe(32)
    
    def is_safe_filename(self, filename):
        """Prüfe ob Dateiname sicher ist"""
        if not filename:
            return False
        
        # Sichere Dateinamen
        filename = secure_filename(filename)
        
        # Prüfe Dateiendung
        if '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.allowed_extensions
    
    def validate_text_input(self, text):
        """Validiere Text-Eingabe"""
        if not text or not isinstance(text, str):
            return False, "Text darf nicht leer sein"
        
        # Maximale Länge prüfen
        max_length = int(os.getenv('MODEL_MAX_LENGTH', 50000))
        if len(text) > max_length:
            return False, f"Text zu lang (max. {max_length} Zeichen)"
        
        # Gefährliche Patterns prüfen
        dangerous_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'javascript:',              # JavaScript URLs
            r'data:text/html',           # Data URLs
            r'vbscript:',                # VBScript
            r'on\w+\s*=',               # Event Handlers
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potentially dangerous content detected: {pattern}")
                return False, "Unerlaubte Inhalte erkannt"
        
        # LaTeX-Injection prüfen
        latex_dangerous = [
            r'\\input\s*\{',
            r'\\include\s*\{',
            r'\\usepackage\s*\{',
            r'\\def\s*\w+',
            r'\\newcommand\s*\w+',
        ]
        
        for pattern in latex_dangerous:
            if re.search(pattern, text):
                logger.warning(f"Potentially dangerous LaTeX command: {pattern}")
                return False, "Unerlaubte LaTeX-Befehle erkannt"
        
        return True, "OK"
    
    def validate_file_size(self, file):
        """Validiere Dateigröße"""
        if not file:
            return False, "Keine Datei hochgeladen"
        
        file.seek(0, 2)  # Ende der Datei
        size = file.tell()
        file.seek(0)     # Zurück zum Anfang
        
        if size > self.max_file_size:
            return False, f"Datei zu groß (max. {self.max_file_size // (1024*1024)}MB)"
        
        return True, "OK"
    
    def check_rate_limit(self):
        """Rate Limiting prüfen"""
        client_ip = request.remote_addr
        current_time = int(time.time())
        
        if client_ip not in self.rate_limit_storage:
            self.rate_limit_storage[client_ip] = []
        
        # Alte Einträge entfernen
        minute_ago = current_time - 60
        self.rate_limit_storage[client_ip] = [
            timestamp for timestamp in self.rate_limit_storage[client_ip]
            if timestamp > minute_ago
        ]
        
        # Rate Limit prüfen
        max_requests = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
        if len(self.rate_limit_storage[client_ip]) >= max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': f'Max {max_requests} requests per minute'
            }), 429
        
        # Request hinzufügen
        self.rate_limit_storage[client_ip].append(current_time)
    
    def sanitize_text(self, text):
        """Text bereinigen und sichern"""
        # HTML-Tags entfernen
        text = re.sub(r'<[^>]+>', '', text)
        
        # Gefährliche Zeichen escapen
        dangerous_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;',
        }
        
        for char, replacement in dangerous_chars.items():
            text = text.replace(char, replacement)
        
        return text.strip()

# Globale Instanz
security_manager = SecurityManager()

def require_security_validation(f):
    """Decorator für Sicherheitsvalidierung"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Rate Limiting wird automatisch durch before_request gehandhabt
        
        # Text-Validierung
        if 'text' in request.form:
            text = request.form['text']
            is_valid, message = security_manager.validate_text_input(text)
            if not is_valid:
                return jsonify({'error': message}), 400
        
        # File-Validierung
        if 'file' in request.files:
            file = request.files['file']
            
            # Dateiname prüfen
            if not security_manager.is_safe_filename(file.filename):
                return jsonify({'error': 'Unerlaubte Dateiendung'}), 400
            
            # Dateigröße prüfen
            is_valid, message = security_manager.validate_file_size(file)
            if not is_valid:
                return jsonify({'error': message}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_latex_content(content):
    """Validiere LaTeX-Inhalt auf Sicherheit"""
    dangerous_commands = [
        r'\\write18',      # Shell execution
        r'\\immediate\s*\\write18',
        r'\\input\s*\{',   # File inclusion
        r'\\include\s*\{',
        r'\\catcode',      # Character code changes
        r'\\def\s*\\',     # Command redefinition
        r'\\let\s*\\',     # Command assignment
    ]
    
    for pattern in dangerous_commands:
        if re.search(pattern, content, re.IGNORECASE):
            logger.error(f"Dangerous LaTeX command detected: {pattern}")
            return False, f"Gefährlicher LaTeX-Befehl erkannt: {pattern}"
    
    return True, "OK"

def generate_csrf_token():
    """Generiere CSRF-Token"""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token, session_token):
    """Verifiziere CSRF-Token"""
    return secrets.compare_digest(token, session_token)

# Import time module für Rate Limiting
import time
