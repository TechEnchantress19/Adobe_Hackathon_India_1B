"""
Internationalization (i18n) utilities for the Persona-Driven PDF Analysis System
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class I18n:
    """Internationalization handler"""
    
    def __init__(self, default_locale: str = 'en'):
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations = {}
        self.locales_dir = Path(__file__).parent.parent / 'locales'
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        if not self.locales_dir.exists():
            return
        
        for locale_file in self.locales_dir.glob('*.json'):
            locale_code = locale_file.stem
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.translations[locale_code] = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load locale {locale_code}: {e}")
    
    def set_locale(self, locale: str):
        """Set the current locale"""
        if locale in self.translations:
            self.current_locale = locale
        else:
            print(f"Warning: Locale '{locale}' not found, using default '{self.default_locale}'")
            self.current_locale = self.default_locale
    
    def get_available_locales(self) -> list:
        """Get list of available locales"""
        return list(self.translations.keys())
    
    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key with optional formatting
        
        Args:
            key: Translation key in dot notation (e.g., 'ui.title')
            **kwargs: Variables for string formatting
        
        Returns:
            Translated string
        """
        # Get translation from current locale
        translation = self._get_nested_value(
            self.translations.get(self.current_locale, {}), 
            key
        )
        
        # Fallback to default locale if not found
        if translation is None and self.current_locale != self.default_locale:
            translation = self._get_nested_value(
                self.translations.get(self.default_locale, {}),
                key
            )
        
        # Final fallback to key itself
        if translation is None:
            translation = key
        
        # Format with provided kwargs
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError as e:
                print(f"Warning: Missing format variable {e} for key '{key}'")
        
        return translation
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """Get nested dictionary value using dot notation"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def get_persona_translations(self) -> Dict[str, str]:
        """Get all persona translations for current locale"""
        personas = self.translations.get(self.current_locale, {}).get('personas', {})
        if not personas and self.current_locale != self.default_locale:
            personas = self.translations.get(self.default_locale, {}).get('personas', {})
        return personas
    
    def get_job_translations(self) -> Dict[str, str]:
        """Get all job translations for current locale"""
        jobs = self.translations.get(self.current_locale, {}).get('jobs', {})
        if not jobs and self.current_locale != self.default_locale:
            jobs = self.translations.get(self.default_locale, {}).get('jobs', {})
        return jobs

# Global i18n instance
i18n = I18n()

def detect_language_from_text(text: str) -> str:
    """
    Simple language detection based on character patterns
    Returns ISO language code (en, es, fr, zh, etc.)
    """
    if not text:
        return 'en'
    
    # Count character types
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    total_chars = len(text.replace(' ', ''))
    
    if total_chars > 0:
        chinese_ratio = chinese_chars / total_chars
        if chinese_ratio > 0.3:
            return 'zh'
    
    # Check for common Spanish words/patterns
    spanish_indicators = ['ción', 'mente', 'que', 'para', 'con', 'una', 'los', 'las', 'del', 'ñ']
    spanish_count = sum(1 for indicator in spanish_indicators if indicator in text.lower())
    
    # Check for common French words/patterns
    french_indicators = ['que', 'pour', 'avec', 'dans', 'sur', 'être', 'avoir', 'tion', 'ç', 'à', 'è', 'é']
    french_count = sum(1 for indicator in french_indicators if indicator in text.lower())
    
    # Simple heuristic
    if spanish_count > french_count and spanish_count > 2:
        return 'es'
    elif french_count > 2:
        return 'fr'
    
    return 'en'  # Default to English

def get_locale_from_browser(accept_language: str) -> str:
    """
    Parse browser Accept-Language header to determine preferred locale
    """
    if not accept_language:
        return 'en'
    
    # Parse Accept-Language header (e.g., "en-US,en;q=0.9,es;q=0.8")
    languages = []
    for lang_range in accept_language.split(','):
        lang_range = lang_range.strip()
        if ';' in lang_range:
            lang, quality = lang_range.split(';', 1)
            try:
                q = float(quality.split('=')[1])
            except (IndexError, ValueError):
                q = 1.0
        else:
            lang, q = lang_range, 1.0
        
        # Extract primary language code
        primary_lang = lang.split('-')[0].lower()
        languages.append((primary_lang, q))
    
    # Sort by quality score
    languages.sort(key=lambda x: x[1], reverse=True)
    
    # Return first supported language
    available_locales = i18n.get_available_locales()
    for lang, _ in languages:
        if lang in available_locales:
            return lang
    
    return 'en'  # Default to English