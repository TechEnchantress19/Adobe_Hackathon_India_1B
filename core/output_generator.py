"""
Output generation module for creating structured JSON results
Handles persona-adaptive headings and detailed summaries
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from .persona_analyzer import PersonaAnalyzer


class OutputGenerator:
    """Generates structured output with persona-adaptive content"""
    
    def __init__(self):
        self.persona_analyzer = PersonaAnalyzer()
    
    def generate_output(self, documents: List[Dict], persona: str, job_to_be_done: str,
                       ranked_sections: List[Dict], persona_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete output structure matching Round 1B specifications
        
        Args:
            documents: List of processed documents
            persona: User-specified persona
            job_to_be_done: User-specified job description
            ranked_sections: Ranked sections from ranking engine
            persona_context: Persona analysis context
            
        Returns:
            Complete JSON output structure
        """
        
        # Generate metadata
        metadata = self._generate_metadata(documents, persona, job_to_be_done)
        
        # Generate extracted sections with adaptive headings
        extracted_sections = self._generate_extracted_sections(ranked_sections, persona_context)
        
        # Generate subsection analysis
        subsection_analysis = self._generate_subsection_analysis(ranked_sections, documents, persona_context)
        
        return {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
    
    def _generate_metadata(self, documents: List[Dict], persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Generate metadata section"""
        input_documents = []
        
        for doc in documents:
            doc_info = {
                "filename": doc.get('filename', 'unknown'),
                "pages": len(doc.get('pages', [])),
                "has_tables": len(doc.get('tables', [])) > 0,
                "sections_found": len(doc.get('sections', []))
            }
            
            # Add outline info if available
            if doc.get('outline'):
                doc_info["outline_items"] = len(doc['outline'])
            
            input_documents.append(doc_info)
        
        return {
            "input_documents": input_documents,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "timestamp": datetime.now().isoformat(),
            "processing_summary": {
                "total_documents": len(documents),
                "total_sections_analyzed": len([s for doc in documents for s in doc.get('sections', [])]),
                "total_tables_found": sum(len(doc.get('tables', [])) for doc in documents)
            }
        }
    
    def _generate_extracted_sections(self, ranked_sections: List[Dict], persona_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate extracted sections with adaptive headings"""
        extracted = []
        
        for section in ranked_sections:
            # Generate adaptive heading
            original_title = section.get('title', '')
            adaptive_title = self.persona_analyzer.generate_adaptive_heading(
                original_title, persona_context
            )
            
            extracted_section = {
                "document": section.get('document', ''),
                "page_number": section.get('page', 1),
                "original_section_title": original_title,
                "persona_adapted_title": adaptive_title,
                "importance_rank": section.get('importance_rank', 0),
                "relevance_scores": {
                    "semantic_similarity": section.get('semantic_score', 0),
                    "keyword_match": section.get('keyword_score', 0),
                    "heading_weight": section.get('heading_score', 0),
                    "positional_score": section.get('positional_score', 0),
                    "content_quality": section.get('quality_score', 0),
                    "total_score": section.get('total_score', 0)
                },
                "content_preview": section.get('content', '')[:200] + "..." if len(section.get('content', '')) > 200 else section.get('content', ''),
                "word_count": section.get('word_count', 0),
                "has_tables": section.get('has_tables', False)
            }
            
            extracted.append(extracted_section)
        
        return extracted
    
    def _generate_subsection_analysis(self, ranked_sections: List[Dict], documents: List[Dict], 
                                    persona_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed subsection analysis with refined summaries"""
        subsections = []
        
        # Get table data for reference
        table_data = {}
        for doc in documents:
            doc_filename = doc.get('filename', '')
            table_data[doc_filename] = doc.get('tables', [])
        
        # Process top sections for detailed analysis
        top_sections = ranked_sections[:15]  # Limit to top 15 for detailed analysis
        
        for section in top_sections:
            doc_filename = section.get('document', '')
            page_num = section.get('page', 1)
            
            # Get tables for this page/section
            relevant_tables = [
                table for table in table_data.get(doc_filename, [])
                if table.get('page') == page_num
            ]
            
            # Generate refined summary
            refined_text = self._generate_refined_summary(section, persona_context, relevant_tables)
            
            subsection = {
                "document": doc_filename,
                "page_number": page_num,
                "section_title": section.get('title', ''),
                "persona_adapted_title": self.persona_analyzer.generate_adaptive_heading(
                    section.get('title', ''), persona_context
                ),
                "refined_text": refined_text,
                "importance_rank": section.get('importance_rank', 0),
                "actionable_insights": self._generate_actionable_insights(section, persona_context),
                "table_integration": self._integrate_table_data(relevant_tables) if relevant_tables else None
            }
            
            subsections.append(subsection)
        
        return subsections
    
    def _generate_refined_summary(self, section: Dict, persona_context: Dict[str, Any], 
                                tables: List[Dict]) -> str:
        """Generate persona-specific refined summary"""
        content = section.get('content', '')
        title = section.get('title', '')
        persona_type = persona_context.get('persona_type', 'general')
        job_keywords = persona_context.get('action_words', [])
        
        if not content:
            return "No content available for analysis."
        
        # Split content into sentences for analysis
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        # Select most relevant sentences based on persona
        relevant_sentences = []
        persona_keywords = persona_context.get('keywords', [])
        
        for sentence in sentences[:10]:  # Limit to first 10 sentences
            sentence_lower = sentence.lower()
            
            # Score sentence relevance
            relevance_score = 0
            for keyword in persona_keywords[:20]:  # Top 20 keywords
                if keyword.lower() in sentence_lower:
                    relevance_score += 1
            
            if relevance_score > 0:
                relevant_sentences.append((sentence, relevance_score))
        
        # Sort by relevance and take top sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        selected_sentences = [s[0] for s in relevant_sentences[:5]]
        
        if not selected_sentences:
            # Fallback to first few sentences
            selected_sentences = sentences[:3]
        
        # Create refined summary
        summary = '. '.join(selected_sentences)
        
        # Add persona-specific context
        persona_prefix = self._get_persona_prefix(persona_type, job_keywords)
        if persona_prefix:
            summary = f"{persona_prefix}: {summary}"
        
        # Add table reference if relevant
        if tables:
            summary += f" This section includes {len(tables)} relevant table(s) with structured data."
        
        return summary
    
    def _get_persona_prefix(self, persona_type: str, job_keywords: List[str]) -> str:
        """Get persona-specific prefix for summaries"""
        prefixes = {
            'hr': {
                'create': "For HR form creation and management",
                'manage': "For employee lifecycle management",
                'default': "For HR professionals"
            },
            'student': {
                'study': "For exam preparation and learning",
                'analyze': "For academic analysis and understanding",
                'default': "For educational purposes"
            },
            'analyst': {
                'analyze': "For data analysis and insights",
                'create': "For report and visualization development",
                'default': "For analytical work"
            }
        }
        
        if persona_type in prefixes:
            persona_prefixes = prefixes[persona_type]
            
            # Match with job keywords
            for keyword in job_keywords:
                if keyword in persona_prefixes:
                    return persona_prefixes[keyword]
            
            # Default for persona type
            return persona_prefixes['default']
        
        return ""
    
    def _generate_actionable_insights(self, section: Dict, persona_context: Dict[str, Any]) -> List[str]:
        """Generate actionable insights based on persona and content"""
        insights = []
        content = section.get('content', '').lower()
        persona_type = persona_context.get('persona_type', 'general')
        job_words = persona_context.get('action_words', [])
        
        # Persona-specific insight templates
        if persona_type == 'hr':
            if 'form' in content and 'create' in job_words:
                insights.append("Consider implementing digital form templates with e-signature capabilities")
                insights.append("Ensure compliance with data privacy regulations when collecting employee information")
            
            if 'process' in content:
                insights.append("Streamline workflow by identifying bottlenecks and automation opportunities")
            
            if 'employee' in content:
                insights.append("Focus on user experience to improve employee satisfaction and adoption")
        
        elif persona_type == 'student':
            if 'exam' in content or 'test' in content:
                insights.append("Create focused study materials highlighting key concepts and examples")
                insights.append("Develop practice questions based on the identified learning objectives")
            
            if 'concept' in content or 'theory' in content:
                insights.append("Break down complex concepts into digestible learning modules")
                insights.append("Use visual aids and examples to reinforce understanding")
        
        elif persona_type == 'analyst':
            if 'data' in content or 'analysis' in content:
                insights.append("Develop dashboards and visualizations to track key performance indicators")
                insights.append("Implement automated reporting to provide real-time insights")
            
            if 'trend' in content or 'pattern' in content:
                insights.append("Use predictive analytics to forecast future trends and outcomes")
                insights.append("Establish baseline metrics for comparative analysis")
        
        # Generic insights based on content
        if section.get('has_tables'):
            insights.append("Leverage structured data for automated processing and analysis")
        
        if section.get('word_count', 0) > 200:
            insights.append("Consider summarizing key points for quick reference and decision-making")
        
        # Ensure we have at least some insights
        if not insights:
            insights = [
                "Review this section for relevant information and best practices",
                "Consider how this content applies to your specific use case",
                "Look for implementation opportunities in your workflow"
            ]
        
        return insights[:3]  # Limit to top 3 insights
    
    def _integrate_table_data(self, tables: List[Dict]) -> Dict[str, Any] | None:
        """Integrate and summarize table data"""
        if not tables:
            return None
        
        table_summary = {
            "table_count": len(tables),
            "total_rows": 0,
            "total_columns": 0,
            "table_details": []
        }
        
        for i, table in enumerate(tables):
            table_data = table.get('data', [])
            headers = table.get('headers', [])
            
            rows = len(table_data)
            cols = len(headers) if headers else 0
            
            table_summary["total_rows"] += rows
            table_summary["total_columns"] += cols
            
            table_detail = {
                "table_index": i + 1,
                "rows": rows,
                "columns": cols,
                "headers": headers[:5] if headers else [],  # First 5 headers
                "source": table.get('source', 'unknown'),
                "sample_data": table_data[:2] if table_data else []  # First 2 rows
            }
            
            table_summary["table_details"].append(table_detail)
        
        return table_summary
