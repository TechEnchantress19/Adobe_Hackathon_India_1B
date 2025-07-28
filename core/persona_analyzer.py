"""
Persona analysis module for understanding user context and generating persona-specific insights
"""

import re
from typing import Dict, List, Any, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np


class PersonaAnalyzer:
    """Analyzes persona and job-to-be-done to create context for content ranking"""
    
    def __init__(self):
        # Initialize lightweight sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # ~90MB model
        
        # Persona-specific keywords and concepts
        self.persona_keywords = {
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
        
        # Job-specific action keywords
        self.action_keywords = {
            'create': ['design', 'build', 'develop', 'generate', 'make', 'construct'],
            'manage': ['organize', 'coordinate', 'oversee', 'control', 'administer', 'handle'],
            'analyze': ['examine', 'study', 'investigate', 'review', 'assess', 'evaluate'],
            'implement': ['execute', 'deploy', 'establish', 'install', 'setup', 'configure'],
            'optimize': ['improve', 'enhance', 'streamline', 'refine', 'upgrade', 'efficiency']
        }
    
    def analyze_persona(self, persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """
        Analyze persona and job to create context for content ranking
        
        Args:
            persona: User-specified persona (e.g., "HR professional")
            job_to_be_done: User-specified job description
            
        Returns:
            Dictionary containing persona analysis and context
        """
        persona_lower = persona.lower()
        job_lower = job_to_be_done.lower()
        
        # Identify persona type
        persona_type = self._identify_persona_type(persona_lower)
        
        # Extract action words from job
        action_words = self._extract_action_words(job_lower)
        
        # Generate persona-specific keywords
        keywords = self._generate_keywords(persona_type, job_lower)
        
        # Create semantic embeddings
        persona_embedding = self.model.encode(persona)
        job_embedding = self.model.encode(job_to_be_done)
        combined_embedding = self.model.encode(f"{persona} {job_to_be_done}")
        
        # Generate heading templates
        heading_templates = self._generate_heading_templates(persona_type, action_words)
        
        return {
            'persona': persona,
            'job_to_be_done': job_to_be_done,
            'persona_type': persona_type,
            'action_words': action_words,
            'keywords': keywords,
            'persona_embedding': persona_embedding,
            'job_embedding': job_embedding,
            'combined_embedding': combined_embedding,
            'heading_templates': heading_templates
        }
    
    def _identify_persona_type(self, persona: str) -> str:
        """Identify the primary persona type from input"""
        for persona_type, keywords in self.persona_keywords.items():
            if persona_type in persona or any(keyword in persona for keyword in keywords):
                return persona_type
        
        # Default classification based on common terms
        if any(term in persona for term in ['human', 'hr', 'people', 'employee']):
            return 'hr'
        elif any(term in persona for term in ['student', 'learner', 'academic']):
            return 'student'
        elif any(term in persona for term in ['analyst', 'data', 'research']):
            return 'analyst'
        elif any(term in persona for term in ['developer', 'engineer', 'programmer']):
            return 'developer'
        elif any(term in persona for term in ['manager', 'director', 'supervisor']):
            return 'manager'
        else:
            return 'general'
    
    def _extract_action_words(self, job_text: str) -> List[str]:
        """Extract action words and verbs from job description"""
        action_words = []
        
        # Check for main action categories
        for action, synonyms in self.action_keywords.items():
            if action in job_text or any(syn in job_text for syn in synonyms):
                action_words.append(action)
        
        # Extract verbs using simple pattern matching
        verb_patterns = [
            r'\b(create|make|build|develop|design|generate)\b',
            r'\b(manage|organize|coordinate|oversee|handle)\b',
            r'\b(analyze|examine|study|review|assess)\b',
            r'\b(implement|execute|deploy|establish)\b',
            r'\b(optimize|improve|enhance|streamline)\b'
        ]
        
        for pattern in verb_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            action_words.extend(matches)
        
        return list(set(action_words))  # Remove duplicates
    
    def _generate_keywords(self, persona_type: str, job_text: str) -> List[str]:
        """Generate comprehensive keywords for ranking"""
        keywords = []
        
        # Add persona-specific keywords
        if persona_type in self.persona_keywords:
            keywords.extend(self.persona_keywords[persona_type])
        
        # Extract important words from job description
        job_words = re.findall(r'\b[a-zA-Z]{4,}\b', job_text)
        keywords.extend(job_words)
        
        # Add related terms based on context
        context_keywords = self._get_context_keywords(persona_type, job_text)
        keywords.extend(context_keywords)
        
        return list(set(keywords))  # Remove duplicates
    
    def _get_context_keywords(self, persona_type: str, job_text: str) -> List[str]:
        """Get additional context-specific keywords"""
        context_keywords = []
        
        if persona_type == 'hr':
            if 'form' in job_text:
                context_keywords.extend(['template', 'field', 'document', 'signature', 'approval'])
            if 'onboard' in job_text:
                context_keywords.extend(['orientation', 'checklist', 'welcome', 'setup'])
        
        elif persona_type == 'student':
            if 'exam' in job_text or 'test' in job_text:
                context_keywords.extend(['preparation', 'review', 'practice', 'question'])
            if 'study' in job_text:
                context_keywords.extend(['notes', 'summary', 'concept', 'material'])
        
        elif persona_type == 'analyst':
            if 'trend' in job_text:
                context_keywords.extend(['pattern', 'growth', 'decline', 'forecast'])
            if 'data' in job_text:
                context_keywords.extend(['dataset', 'visualization', 'chart', 'graph'])
        
        return context_keywords
    
    def _generate_heading_templates(self, persona_type: str, action_words: List[str]) -> Dict[str, List[str]]:
        """Generate persona-specific heading templates"""
        templates = {
            'hr': {
                'create': [
                    "Onboarding Compliance Forms",
                    "Streamlined E-Signature Workflow",
                    "Employee Documentation Templates",
                    "HR Process Automation",
                    "Digital Form Management"
                ],
                'manage': [
                    "Employee Lifecycle Management",
                    "HR Workflow Optimization",
                    "Compliance Tracking System",
                    "Personnel Record Management",
                    "Policy Administration"
                ]
            },
            'student': {
                'study': [
                    "Exam-Centric Key Concepts",
                    "Simplified Study Guides",
                    "Essential Learning Materials",
                    "Course Summary Framework",
                    "Academic Success Strategies"
                ],
                'analyze': [
                    "Critical Concept Analysis",
                    "Learning Objective Breakdown",
                    "Study Pattern Recognition",
                    "Knowledge Gap Assessment",
                    "Academic Performance Insights"
                ]
            },
            'analyst': {
                'analyze': [
                    "Market Trend Visualizations",
                    "R&D Investment Insights",
                    "Data-Driven Decision Framework",
                    "Performance Analytics Dashboard",
                    "Strategic Business Intelligence"
                ],
                'create': [
                    "Analytical Report Generation",
                    "Predictive Model Development",
                    "Business Intelligence Solutions",
                    "Data Visualization Tools",
                    "Insight Generation Framework"
                ]
            }
        }
        
        # Get templates for the persona type
        persona_templates = templates.get(persona_type, {})
        
        # Return relevant templates based on action words
        relevant_templates = {}
        for action in action_words:
            if action in persona_templates:
                relevant_templates[action] = persona_templates[action]
        
        # If no specific templates found, use generic ones
        if not relevant_templates and persona_templates:
            relevant_templates = persona_templates
        
        return relevant_templates
    
    def generate_adaptive_heading(self, original_heading: str, persona_context: Dict[str, Any]) -> str:
        """
        Generate an adaptive heading based on persona context
        
        Args:
            original_heading: Original section heading from PDF
            persona_context: Persona analysis context
            
        Returns:
            Persona-adapted heading
        """
        persona_type = persona_context['persona_type']
        action_words = persona_context['action_words']
        heading_templates = persona_context['heading_templates']
        
        # If we have specific templates, try to match
        if heading_templates:
            for action, templates in heading_templates.items():
                if action in action_words and templates:
                    # Try to find the most relevant template
                    original_lower = original_heading.lower()
                    
                    # Simple keyword matching to select best template
                    best_template = templates[0]  # Default to first
                    max_matches = 0
                    
                    for template in templates:
                        template_lower = template.lower()
                        matches = sum(1 for word in original_lower.split() 
                                    if word in template_lower)
                        if matches > max_matches:
                            max_matches = matches
                            best_template = template
                    
                    return best_template
        
        # Fallback: enhance original heading with persona context
        return self._enhance_heading(original_heading, persona_context)
    
    def _enhance_heading(self, heading: str, persona_context: Dict[str, Any]) -> str:
        """Enhance original heading with persona-specific language"""
        persona_type = persona_context['persona_type']
        
        # Persona-specific prefixes
        prefixes = {
            'hr': ['Employee-Focused', 'Compliance-Ready', 'Workflow-Optimized'],
            'student': ['Study-Oriented', 'Exam-Focused', 'Learning-Centered'],
            'analyst': ['Data-Driven', 'Insight-Rich', 'Analytics-Based'],
            'developer': ['Implementation-Ready', 'Technical', 'Development-Focused'],
            'manager': ['Strategic', 'Management-Oriented', 'Decision-Supporting']
        }
        
        # Persona-specific suffixes
        suffixes = {
            'hr': ['for HR Excellence', 'in Workplace Management', 'for Employee Success'],
            'student': ['for Academic Success', 'in Learning Context', 'for Exam Preparation'],
            'analyst': ['for Business Intelligence', 'in Data Analysis', 'for Strategic Insights'],
            'developer': ['for Development Teams', 'in Technical Implementation', 'for System Design'],
            'manager': ['for Leadership Decisions', 'in Strategic Planning', 'for Team Management']
        }
        
        if persona_type in prefixes:
            prefix = prefixes[persona_type][0]  # Use first prefix
            suffix = suffixes[persona_type][0]  # Use first suffix
            return f"{prefix} {heading} {suffix}"
        
        return heading
