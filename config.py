"""
Configuration settings for the Persona-Driven PDF Analysis System
"""

import os
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/tmp/uploads'
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Processing settings
    MAX_PROCESSING_TIME = int(os.environ.get('MAX_PROCESSING_TIME', '300'))  # 5 minutes timeout
    MAX_FILES_PER_REQUEST = int(os.environ.get('MAX_FILES_PER_REQUEST', '10'))
    
    # Model settings
    SENTENCE_TRANSFORMER_MODEL = os.environ.get('SENTENCE_TRANSFORMER_MODEL', 'all-MiniLM-L6-v2')
    MODEL_CACHE_DIR = os.environ.get('MODEL_CACHE_DIR') or str(Path.home() / '.cache' / 'sentence-transformers')
    
    # Ranking engine settings
    RANKING_WEIGHTS = {
        'semantic_similarity': float(os.environ.get('WEIGHT_SEMANTIC', '0.35')),
        'keyword_match': float(os.environ.get('WEIGHT_KEYWORD', '0.25')),
        'heading_type': float(os.environ.get('WEIGHT_HEADING', '0.20')),
        'positional_score': float(os.environ.get('WEIGHT_POSITION', '0.10')),
        'content_quality': float(os.environ.get('WEIGHT_QUALITY', '0.10'))
    }
    
    # Content extraction settings
    MAX_SECTION_LENGTH = int(os.environ.get('MAX_SECTION_LENGTH', '1000'))
    MIN_SECTION_WORDS = int(os.environ.get('MIN_SECTION_WORDS', '10'))
    MAX_SECTIONS_PER_DOCUMENT = int(os.environ.get('MAX_SECTIONS_PER_DOCUMENT', '50'))
    
    # Table extraction settings
    CAMELOT_LATTICE_ENABLED = os.environ.get('CAMELOT_LATTICE_ENABLED', 'True').lower() == 'true'
    CAMELOT_STREAM_ENABLED = os.environ.get('CAMELOT_STREAM_ENABLED', 'True').lower() == 'true'
    MIN_TABLE_ROWS = int(os.environ.get('MIN_TABLE_ROWS', '2'))
    MIN_TABLE_COLS = int(os.environ.get('MIN_TABLE_COLS', '2'))
    
    # Output settings
    MAX_EXTRACTED_SECTIONS = int(os.environ.get('MAX_EXTRACTED_SECTIONS', '50'))
    MAX_SUBSECTION_ANALYSIS = int(os.environ.get('MAX_SUBSECTION_ANALYSIS', '15'))
    MAX_INSIGHTS_PER_SECTION = int(os.environ.get('MAX_INSIGHTS_PER_SECTION', '3'))
    
    # Performance settings
    ENABLE_MULTIPROCESSING = os.environ.get('ENABLE_MULTIPROCESSING', 'False').lower() == 'true'
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '2'))
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE')
    
    # CLI mode specific settings
    CLI_INPUT_DIR = os.environ.get('CLI_INPUT_DIR', '/app/input')
    CLI_OUTPUT_DIR = os.environ.get('CLI_OUTPUT_DIR', '/app/output')
    
    # Web mode specific settings
    WEB_HOST = os.environ.get('WEB_HOST', '0.0.0.0')
    WEB_PORT = int(os.environ.get('WEB_PORT', '8000'))
    
    # Persona analysis settings
    DEFAULT_PERSONA_KEYWORDS = {
        'hr': [
            'onboarding', 'compliance', 'forms', 'employee', 'hiring', 'recruitment',
            'benefits', 'payroll', 'performance', 'policies', 'training', 'documentation',
            'workflow', 'process', 'management', 'human resources', 'staff', 'personnel'
        ],
        'student': [
            'study', 'exam', 'course', 'learning', 'education', 'assignment', 'grade',
            'curriculum', 'syllabus', 'lecture', 'tutorial', 'research', 'academic',
            'knowledge', 'concept', 'theory', 'practical', 'skill', 'understanding'
        ],
        'analyst': [
            'data', 'analysis', 'trend', 'insight', 'metric', 'report', 'dashboard',
            'visualization', 'statistics', 'model', 'prediction', 'pattern', 'research',
            'investment', 'market', 'performance', 'roi', 'kpi', 'business intelligence'
        ],
        'developer': [
            'code', 'programming', 'api', 'framework', 'database', 'application',
            'software', 'development', 'integration', 'testing', 'deployment',
            'architecture', 'design', 'implementation', 'documentation', 'technical'
        ],
        'manager': [
            'strategy', 'planning', 'execution', 'team', 'leadership', 'decision',
            'project', 'goal', 'objective', 'budget', 'resource', 'stakeholder',
            'communication', 'coordination', 'oversight', 'responsibility'
        ]
    }
    
    # Advanced processing options
    ENABLE_MULTILINGUAL_SUPPORT = os.environ.get('ENABLE_MULTILINGUAL_SUPPORT', 'True').lower() == 'true'
    TEXT_PREPROCESSING_ENABLED = os.environ.get('TEXT_PREPROCESSING_ENABLED', 'True').lower() == 'true'
    ADAPTIVE_HEADING_GENERATION = os.environ.get('ADAPTIVE_HEADING_GENERATION', 'True').lower() == 'true'
    
    # Memory management
    MAX_MEMORY_PER_DOCUMENT = int(os.environ.get('MAX_MEMORY_PER_DOCUMENT', '100'))  # MB
    GARBAGE_COLLECTION_THRESHOLD = int(os.environ.get('GC_THRESHOLD', '10'))
    
    # Cache settings
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'False').lower() == 'true'
    CACHE_TTL = int(os.environ.get('CACHE_TTL', '3600'))  # 1 hour
    
    @staticmethod
    def validate_config():
        """Validate configuration settings"""
        errors = []
        
        # Validate weight sum
        weight_sum = sum(Config.RANKING_WEIGHTS.values())
        if abs(weight_sum - 1.0) > 0.01:
            errors.append(f"Ranking weights sum to {weight_sum:.3f}, should be 1.0")
        
        # Validate file size limits
        if Config.MAX_CONTENT_LENGTH > 100 * 1024 * 1024:  # 100MB
            errors.append("MAX_CONTENT_LENGTH exceeds recommended 100MB limit")
        
        # Validate processing limits
        if Config.MAX_PROCESSING_TIME > 600:  # 10 minutes
            errors.append("MAX_PROCESSING_TIME exceeds recommended 10 minute limit")
        
        # Validate directory paths
        if not os.path.exists(os.path.dirname(Config.CLI_INPUT_DIR)):
            errors.append(f"CLI input directory parent does not exist: {Config.CLI_INPUT_DIR}")
        
        if not os.path.exists(os.path.dirname(Config.CLI_OUTPUT_DIR)):
            errors.append(f"CLI output directory parent does not exist: {Config.CLI_OUTPUT_DIR}")
        
        return errors
    
    @staticmethod
    def create_directories():
        """Create necessary directories"""
        directories = [
            Config.UPLOAD_FOLDER,
            Config.CLI_INPUT_DIR,
            Config.CLI_OUTPUT_DIR,
            Config.MODEL_CACHE_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def get_model_config():
        """Get model-specific configuration"""
        return {
            'model_name': Config.SENTENCE_TRANSFORMER_MODEL,
            'cache_folder': Config.MODEL_CACHE_DIR,
            'device': 'cpu',  # Force CPU usage as per requirements
            'show_progress_bar': False
        }
    
    @staticmethod
    def get_pdf_processing_config():
        """Get PDF processing configuration"""
        return {
            'enable_camelot_lattice': Config.CAMELOT_LATTICE_ENABLED,
            'enable_camelot_stream': Config.CAMELOT_STREAM_ENABLED,
            'min_table_rows': Config.MIN_TABLE_ROWS,
            'min_table_cols': Config.MIN_TABLE_COLS,
            'max_section_length': Config.MAX_SECTION_LENGTH,
            'min_section_words': Config.MIN_SECTION_WORDS,
            'max_sections_per_doc': Config.MAX_SECTIONS_PER_DOCUMENT
        }
    
    @staticmethod
    def get_ranking_config():
        """Get ranking engine configuration"""
        return {
            'weights': Config.RANKING_WEIGHTS,
            'max_extracted_sections': Config.MAX_EXTRACTED_SECTIONS,
            'score_threshold': 0.1  # Minimum score to include section
        }
    
    @staticmethod
    def get_output_config():
        """Get output generation configuration"""
        return {
            'max_subsection_analysis': Config.MAX_SUBSECTION_ANALYSIS,
            'max_insights_per_section': Config.MAX_INSIGHTS_PER_SECTION,
            'enable_adaptive_headings': Config.ADAPTIVE_HEADING_GENERATION,
            'include_table_data': True
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Stricter limits for production
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    MAX_FILES_PER_REQUEST = 5
    MAX_PROCESSING_TIME = 180  # 3 minutes


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Relaxed limits for testing
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    MAX_PROCESSING_TIME = 60  # 1 minute


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}


def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_map.get(config_name, Config)


# Performance monitoring configuration
PERFORMANCE_CONFIG = {
    'enable_timing': os.environ.get('ENABLE_TIMING', 'True').lower() == 'true',
    'enable_memory_monitoring': os.environ.get('ENABLE_MEMORY_MONITORING', 'False').lower() == 'true',
    'log_slow_operations': True,
    'slow_operation_threshold': 5.0  # seconds
}

# Feature flags
FEATURE_FLAGS = {
    'enable_advanced_ranking': os.environ.get('ENABLE_ADVANCED_RANKING', 'True').lower() == 'true',
    'enable_table_extraction': os.environ.get('ENABLE_TABLE_EXTRACTION', 'True').lower() == 'true',
    'enable_multilingual': os.environ.get('ENABLE_MULTILINGUAL', 'True').lower() == 'true',
    'enable_caching': os.environ.get('ENABLE_CACHING', 'False').lower() == 'true',
    'enable_async_processing': os.environ.get('ENABLE_ASYNC_PROCESSING', 'False').lower() == 'true'
}
