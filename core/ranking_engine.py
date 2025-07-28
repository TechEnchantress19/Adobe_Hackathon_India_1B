"""
Advanced ranking engine for persona-driven content prioritization
Implements multi-factor scoring with semantic similarity, keyword matching, and positional weighting
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re


class RankingEngine:
    """Advanced ranking engine with multi-factor scoring algorithm"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Scoring weights
        self.weights = {
            'semantic_similarity': 0.35,
            'keyword_match': 0.25,
            'heading_type': 0.20,
            'positional_score': 0.10,
            'content_quality': 0.10
        }
        
        # Heading level weights (higher = more important)
        self.heading_weights = {
            1: 1.0,  # H1 - highest importance
            2: 0.8,  # H2
            3: 0.6   # H3
        }
    
    def rank_sections(self, documents: List[Dict], persona_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank all sections across documents using multi-factor scoring
        
        Args:
            documents: List of processed document data
            persona_context: Persona analysis context
            
        Returns:
            List of ranked sections with scores
        """
        all_sections = []
        
        # Collect all sections from all documents
        for doc in documents:
            doc_sections = doc.get('sections', [])
            for section in doc_sections:
                section['document'] = doc['filename']
                all_sections.append(section)
        
        if not all_sections:
            return []
        
        # Calculate scores for all sections
        scored_sections = []
        for section in all_sections:
            score_data = self._calculate_section_score(section, persona_context)
            section.update(score_data)
            scored_sections.append(section)
        
        # Sort by total score (descending)
        scored_sections.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        # Add ranking information
        for rank, section in enumerate(scored_sections, 1):
            section['importance_rank'] = rank
        
        return scored_sections
    
    def _calculate_section_score(self, section: Dict, persona_context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive score for a section"""
        
        # Get section content for analysis
        title = section.get('title', '')
        content = section.get('content', '')
        combined_text = f"{title} {content}"
        
        # 1. Semantic Similarity Score
        semantic_score = self._calculate_semantic_similarity(
            combined_text, persona_context
        )
        
        # 2. Keyword Match Score
        keyword_score = self._calculate_keyword_match(
            combined_text, persona_context['keywords']
        )
        
        # 3. Heading Type Score
        heading_score = self._calculate_heading_score(section)
        
        # 4. Positional Score
        positional_score = self._calculate_positional_score(section)
        
        # 5. Content Quality Score
        quality_score = self._calculate_content_quality(section)
        
        # Calculate weighted total score
        total_score = (
            semantic_score * self.weights['semantic_similarity'] +
            keyword_score * self.weights['keyword_match'] +
            heading_score * self.weights['heading_type'] +
            positional_score * self.weights['positional_score'] +
            quality_score * self.weights['content_quality']
        )
        
        return {
            'semantic_score': round(semantic_score, 4),
            'keyword_score': round(keyword_score, 4),
            'heading_score': round(heading_score, 4),
            'positional_score': round(positional_score, 4),
            'quality_score': round(quality_score, 4),
            'total_score': round(total_score, 4)
        }
    
    def _calculate_semantic_similarity(self, text: str, persona_context: Dict) -> float:
        """Calculate semantic similarity with persona and job context"""
        if not text.strip():
            return 0.0
        
        try:
            # Encode the section text
            text_embedding = self.model.encode([text])
            
            # Calculate similarities with different aspects
            persona_sim = cosine_similarity(
                text_embedding, 
                [persona_context['persona_embedding']]
            )[0][0]
            
            job_sim = cosine_similarity(
                text_embedding,
                [persona_context['job_embedding']]
            )[0][0]
            
            combined_sim = cosine_similarity(
                text_embedding,
                [persona_context['combined_embedding']]
            )[0][0]
            
            # Weighted combination of similarities
            final_similarity = (
                persona_sim * 0.3 +
                job_sim * 0.4 +
                combined_sim * 0.3
            )
            
            return max(0, final_similarity)  # Ensure non-negative
            
        except Exception as e:
            print(f"Semantic similarity calculation error: {e}")
            return 0.0
    
    def _calculate_keyword_match(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword match score with TF-IDF-like weighting"""
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower()
        text_words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Calculate match scores
        exact_matches = 0
        partial_matches = 0
        total_keyword_weight = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_weight = 1.0
            
            # Exact keyword match
            if keyword_lower in text_lower:
                exact_matches += keyword_weight
                total_keyword_weight += keyword_weight
            
            # Partial matches (keyword appears as part of words)
            elif any(keyword_lower in word for word in text_words):
                partial_matches += keyword_weight * 0.5
                total_keyword_weight += keyword_weight
            
            # Stemmed matching (simple suffix removal)
            else:
                keyword_stem = keyword_lower.rstrip('s').rstrip('ed').rstrip('ing')
                if any(keyword_stem in word for word in text_words):
                    partial_matches += keyword_weight * 0.3
                    total_keyword_weight += keyword_weight
        
        if total_keyword_weight == 0:
            return 0.0
        
        # Combine exact and partial matches
        match_score = (exact_matches + partial_matches) / len(keywords)
        
        # Boost score for higher keyword density
        text_word_count = len(text_words)
        if text_word_count > 0:
            density_boost = min(1.0, total_keyword_weight / text_word_count * 10)
            match_score = match_score * (1 + density_boost * 0.2)
        
        return min(1.0, match_score)  # Cap at 1.0
    
    def _calculate_heading_score(self, section: Dict) -> float:
        """Calculate score based on heading level and characteristics"""
        level = section.get('level', 3)
        title = section.get('title', '')
        
        # Base score from heading level
        base_score = self.heading_weights.get(level, 0.4)
        
        # Boost for important heading patterns
        title_lower = title.lower()
        
        # Important words that suggest relevance
        important_patterns = [
            r'\b(introduction|overview|summary|conclusion)\b',
            r'\b(method|approach|process|workflow)\b',
            r'\b(result|finding|outcome|insight)\b',
            r'\b(requirement|specification|guideline)\b',
            r'\b(implementation|solution|strategy)\b'
        ]
        
        pattern_boost = 0.0
        for pattern in important_patterns:
            if re.search(pattern, title_lower):
                pattern_boost += 0.1
        
        # Length penalty for very long titles (likely not true headings)
        length_penalty = 0.0
        if len(title.split()) > 10:
            length_penalty = 0.2
        
        final_score = base_score + pattern_boost - length_penalty
        return max(0.0, min(1.0, final_score))
    
    def _calculate_positional_score(self, section: Dict) -> float:
        """Calculate score based on position in document"""
        page = section.get('page', 1)
        
        # Early pages are generally more important
        if page == 1:
            return 1.0
        elif page <= 3:
            return 0.8
        elif page <= 5:
            return 0.6
        elif page <= 10:
            return 0.4
        else:
            return 0.2
    
    def _calculate_content_quality(self, section: Dict) -> float:
        """Calculate score based on content quality indicators"""
        content = section.get('content', '')
        title = section.get('title', '')
        word_count = section.get('word_count', 0)
        has_tables = section.get('has_tables', False)
        
        quality_score = 0.0
        
        # Word count scoring (sweet spot around 100-500 words)
        if 50 <= word_count <= 500:
            quality_score += 0.4
        elif 20 <= word_count < 50 or 500 < word_count <= 1000:
            quality_score += 0.2
        elif word_count > 1000:
            quality_score += 0.1
        
        # Content structure indicators
        if has_tables:
            quality_score += 0.2
        
        # Check for structured content (lists, numbers)
        if re.search(r'\d+\.|\•|\-\s+', content):
            quality_score += 0.1
        
        # Check for detailed content (presence of specific terms)
        detail_indicators = [
            r'\b(figure|table|chart|graph)\b',
            r'\b(example|instance|case)\b',
            r'\b(step|procedure|instruction)\b',
            r'\b(data|statistic|number|percent)\b'
        ]
        
        for pattern in detail_indicators:
            if re.search(pattern, content.lower()):
                quality_score += 0.05
        
        # Title quality (not too generic)
        generic_titles = ['introduction', 'conclusion', 'summary', 'overview', 'abstract']
        if title.lower() not in generic_titles:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def get_top_sections(self, ranked_sections: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top N sections by importance ranking"""
        return ranked_sections[:limit]
    
    def filter_by_score_threshold(self, ranked_sections: List[Dict], threshold: float = 0.3) -> List[Dict]:
        """Filter sections by minimum total score threshold"""
        return [section for section in ranked_sections 
                if section.get('total_score', 0) >= threshold]
