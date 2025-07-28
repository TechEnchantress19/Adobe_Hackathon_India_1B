"""
Text processing utilities for content analysis and enhancement
"""

import re
import string
from typing import List, Dict, Any, Tuple
import unicodedata


class TextProcessor:
    """Utility class for text processing and analysis"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)
        
        # Fix common PDF extraction issues
        text = self._fix_pdf_artifacts(text)
        
        return text.strip()
    
    def _fix_pdf_artifacts(self, text: str) -> str:
        """Fix common PDF extraction artifacts"""
        # Fix broken words across lines
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
        
        # Fix extra spaces before punctuation
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        
        # Fix missing spaces after punctuation
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        # Remove repeated characters (common in headers)
        text = re.sub(r'(.)\1{3,}', r'\1\1', text)
        
        return text
    
    def extract_keywords(self, text: str, min_length: int = 4, max_keywords: int = 50) -> List[str]:
        """Extract meaningful keywords from text"""
        if not text:
            return []
        
        # Clean and normalize
        text = self.clean_text(text.lower())
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Filter words
        keywords = []
        for word in words:
            if (len(word) >= min_length and 
                word not in self.stop_words and
                not word.isdigit()):
                keywords.append(word)
        
        # Count frequency and return most common
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def extract_sentences(self, text: str, min_length: int = 20) -> List[str]:
        """Extract meaningful sentences from text"""
        if not text:
            return []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= min_length:
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate basic readability metrics"""
        if not text:
            return {'score': 0, 'words': 0, 'sentences': 0, 'avg_words_per_sentence': 0}
        
        # Count words and sentences
        words = len(re.findall(r'\b\w+\b', text))
        sentences = len(re.split(r'[.!?]+', text))
        
        if sentences == 0:
            return {'score': 0, 'words': words, 'sentences': 0, 'avg_words_per_sentence': 0}
        
        avg_words_per_sentence = words / sentences
        
        # Simple readability score (inverse of complexity)
        complexity = avg_words_per_sentence / 20  # Normalize to 0-1 range
        readability_score = max(0, 1 - complexity)
        
        return {
            'score': round(readability_score, 2),
            'words': words,
            'sentences': sentences,
            'avg_words_per_sentence': round(avg_words_per_sentence, 1)
        }
    
    def identify_structure_elements(self, text: str) -> Dict[str, List[str]]:
        """Identify structural elements in text"""
        elements = {
            'numbered_lists': [],
            'bullet_points': [],
            'headings': [],
            'citations': [],
            'urls': []
        }
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Numbered lists
            if re.match(r'^\d+\.?\s+', line):
                elements['numbered_lists'].append(line)
            
            # Bullet points
            elif re.match(r'^[•\-\*]\s+', line):
                elements['bullet_points'].append(line)
            
            # Potential headings (short lines, title case)
            elif (len(line.split()) <= 8 and
                  line[0].isupper() and
                  not line.endswith('.')):
                elements['headings'].append(line)
            
            # Citations (basic pattern)
            elif re.search(r'\(\d{4}\)', line):
                elements['citations'].append(line)
            
            # URLs
            urls = re.findall(r'https?://[^\s]+', line)
            if urls:
                elements['urls'].extend(urls)
        
        return elements
    
    def segment_by_topics(self, text: str, max_segment_length: int = 1000) -> List[Dict[str, Any]]:
        """Segment text into topic-based chunks"""
        if not text:
            return []
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        segments = []
        current_segment = ""
        current_keywords = []
        
        for paragraph in paragraphs:
            # Check if adding this paragraph exceeds length limit
            if len(current_segment) + len(paragraph) > max_segment_length and current_segment:
                # Save current segment
                segments.append({
                    'text': current_segment.strip(),
                    'length': len(current_segment),
                    'keywords': self.extract_keywords(current_segment, max_keywords=10),
                    'readability': self.calculate_readability(current_segment)
                })
                
                # Start new segment
                current_segment = paragraph
            else:
                # Add to current segment
                current_segment += '\n\n' + paragraph if current_segment else paragraph
        
        # Add final segment
        if current_segment:
            segments.append({
                'text': current_segment.strip(),
                'length': len(current_segment),
                'keywords': self.extract_keywords(current_segment, max_keywords=10),
                'readability': self.calculate_readability(current_segment)
            })
        
        return segments
    
    def find_similar_phrases(self, text: str, target_phrase: str, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Find phrases similar to target phrase using simple string matching"""
        if not text or not target_phrase:
            return []
        
        # Extract sentences
        sentences = self.extract_sentences(text)
        
        # Calculate similarity for each sentence
        similar_phrases = []
        target_words = set(target_phrase.lower().split())
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(target_words & sentence_words)
            union = len(target_words | sentence_words)
            
            if union > 0:
                similarity = intersection / union
                if similarity >= threshold:
                    similar_phrases.append((sentence, similarity))
        
        # Sort by similarity
        similar_phrases.sort(key=lambda x: x[1], reverse=True)
        
        return similar_phrases[:10]  # Return top 10
