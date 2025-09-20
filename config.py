"""
Konfigurationsmanagement für LaTeX Converter
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Config:
    """Basis-Konfiguration"""
    
    # Flask-Konfiguration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # 10MB
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Modell-Konfiguration
    MODEL_NAME = os.getenv('MODEL_NAME', 'microsoft/phi-4-mini-instruct')
    MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', './models')
    MODEL_MAX_LENGTH = int(os.getenv('MODEL_MAX_LENGTH', 1024))
    ENABLE_GPU = os.getenv('ENABLE_GPU', 'True').lower() == 'true'
    
    # LaTeX-Konfiguration
    LATEX_COMPILER = os.getenv('LATEX_COMPILER', 'pdflatex')
    LATEX_TIMEOUT = int(os.getenv('LATEX_TIMEOUT', 30))
    LATEX_MAX_ITERATIONS = int(os.getenv('LATEX_MAX_ITERATIONS', 3))
    
    # Sicherheitskonfiguration
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    ALLOWED_FILE_EXTENSIONS = set(os.getenv('ALLOWED_FILE_EXTENSIONS', 'pdf,txt,md').split(','))
    
    # Performance-Konfiguration
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 10))
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 Stunde
    
    # Logging-Konfiguration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    MAX_LOG_SIZE = int(os.getenv('MAX_LOG_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    @classmethod
    def init_app(cls, app):
        """Initialisiere Flask-App mit Konfiguration"""
        app.config.from_object(cls)
        
        # Erstelle Log-Verzeichnis
        log_dir = os.path.dirname(cls.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Erstelle Modell-Cache-Verzeichnis
        if not os.path.exists(cls.MODEL_CACHE_DIR):
            os.makedirs(cls.MODEL_CACHE_DIR)
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validiere Konfiguration und gebe Status zurück"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'config': {}
        }
        
        # Flask-Konfiguration prüfen
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            validation_results['warnings'].append(
                'SECRET_KEY ist noch auf Standardwert - sollte in Produktion geändert werden'
            )
        
        if cls.DEBUG and cls.FLASK_ENV == 'production':
            validation_results['errors'].append(
                'DEBUG sollte in Produktion deaktiviert sein'
            )
            validation_results['valid'] = False
        
        # Modell-Konfiguration prüfen
        try:
            import torch
            if cls.ENABLE_GPU and not torch.cuda.is_available():
                validation_results['warnings'].append(
                    'GPU aktiviert aber nicht verfügbar - CPU wird verwendet'
                )
        except ImportError:
            validation_results['warnings'].append(
                'PyTorch nicht installiert - GPU-Features nicht verfügbar'
            )
        
        # LaTeX-Konfiguration prüfen
        import shutil
        if not shutil.which(cls.LATEX_COMPILER):
            validation_results['errors'].append(
                f'LaTeX-Compiler "{cls.LATEX_COMPILER}" nicht gefunden'
            )
            validation_results['valid'] = False
        
        # Verzeichnisse prüfen
        directories_to_check = [
            cls.MODEL_CACHE_DIR,
            os.path.dirname(cls.LOG_FILE) if cls.LOG_FILE else None
        ]
        
        for directory in directories_to_check:
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    validation_results['config'][f'created_directory_{directory}'] = True
                except Exception as e:
                    validation_results['errors'].append(
                        f'Konnte Verzeichnis "{directory}" nicht erstellen: {e}'
                    )
                    validation_results['valid'] = False
        
        # Konfiguration sammeln
        validation_results['config'].update({
            'model_name': cls.MODEL_NAME,
            'latex_compiler': cls.LATEX_COMPILER,
            'max_content_length': cls.MAX_CONTENT_LENGTH,
            'rate_limit': cls.RATE_LIMIT_PER_MINUTE,
            'log_level': cls.LOG_LEVEL,
            'gpu_enabled': cls.ENABLE_GPU
        })
        
        return validation_results

class DevelopmentConfig(Config):
    """Entwicklungskonfiguration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Schnellere Entwicklung
    MODEL_MAX_LENGTH = 512
    LATEX_TIMEOUT = 10

class ProductionConfig(Config):
    """Produktionskonfiguration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Strenge Sicherheit
    RATE_LIMIT_PER_MINUTE = 30
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    
    # Performance-Optimierungen
    CACHE_TTL = 7200  # 2 Stunden
    MAX_CONCURRENT_REQUESTS = 20

class TestingConfig(Config):
    """Test-Konfiguration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'ERROR'
    
    # Schnelle Tests
    MODEL_MAX_LENGTH = 256
    LATEX_TIMEOUT = 5
    RATE_LIMIT_PER_MINUTE = 1000

# Konfiguration basierend auf Umgebung auswählen
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """Lade Konfiguration basierend auf Umgebung"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])

def load_environment_config():
    """Lade Umgebungsvariablen und gebe Konfiguration zurück"""
    # .env Datei laden falls vorhanden
    env_file = os.getenv('ENV_FILE', '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Umgebungsvariablen aus {env_file} geladen")
    else:
        logger.warning(f"Keine .env Datei gefunden: {env_file}")
    
    # Konfiguration laden und validieren
    app_config = get_config()
    validation = app_config.validate_config()
    
    if not validation['valid']:
        logger.error(f"Konfigurationsfehler: {validation['errors']}")
        raise ValueError(f"Ungültige Konfiguration: {validation['errors']}")
    
    if validation['warnings']:
        for warning in validation['warnings']:
            logger.warning(warning)
    
    logger.info(f"Konfiguration geladen: {validation['config']}")
    return app_config, validation
