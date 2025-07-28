#!/usr/bin/env python3
"""
Demo version of the Persona-Driven PDF Analysis System
This version works with minimal dependencies for demonstration purposes
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

# Try to import dependencies, fall back gracefully if not available
try:
    from flask import Flask, render_template, request, jsonify, session
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available - running without web interface")

# Import i18n utilities
try:
    from utils.i18n import i18n, detect_language_from_text, get_locale_from_browser
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    print("i18n utilities not available - using English only")

def create_demo_app():
    """Create a demo Flask application"""
    if not FLASK_AVAILABLE:
        return None
    
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.secret_key = 'demo_secret_key_for_sessions'
    
    @app.route('/')
    def index():
        # Detect language from browser
        if I18N_AVAILABLE:
            accept_language = request.headers.get('Accept-Language', '')
            detected_locale = get_locale_from_browser(accept_language)
            
            # Use session language if set, otherwise use detected
            current_locale = session.get('locale', detected_locale)
            i18n.set_locale(current_locale)
            
            # Get localized content
            ui_strings = {
                'title': i18n.t('ui.title'),
                'subtitle': i18n.t('ui.subtitle'),
                'persona_label': i18n.t('ui.persona_label'),
                'persona_placeholder': i18n.t('ui.persona_placeholder'),
                'job_label': i18n.t('ui.job_label'),
                'job_placeholder': i18n.t('ui.job_placeholder'),
                'upload_label': i18n.t('ui.upload_label'),
                'upload_help': i18n.t('ui.upload_help'),
                'analyze_button': i18n.t('ui.analyze_button'),
                'example_personas': i18n.t('ui.example_personas'),
                'clear_button': i18n.t('ui.clear_button')
            }
            
            personas = i18n.get_persona_translations()
            jobs = i18n.get_job_translations() 
            available_locales = i18n.get_available_locales()
            
            return render_template('index.html', 
                                 ui=ui_strings, 
                                 personas=personas,
                                 jobs=jobs,
                                 current_locale=current_locale,
                                 available_locales=available_locales)
        else:
            return render_template('index.html')
    
    @app.route('/set_language/<locale>')
    def set_language(locale):
        """Set the interface language"""
        if I18N_AVAILABLE and locale in i18n.get_available_locales():
            session['locale'] = locale
            i18n.set_locale(locale)
        return jsonify({'status': 'success', 'locale': locale})
    
    @app.route('/analyze', methods=['POST'])
    def analyze_demo():
        """Demo analysis endpoint that shows the expected output structure"""
        try:
            # Set language context
            if I18N_AVAILABLE:
                current_locale = session.get('locale', 'en')
                i18n.set_locale(current_locale)
            
            # Get form data
            persona = request.form.get('persona', '').strip()
            job_to_be_done = request.form.get('job_to_be_done', '').strip()
            
            # Auto-detect language from input text if available
            if I18N_AVAILABLE and (persona or job_to_be_done):
                detected_lang = detect_language_from_text(persona + ' ' + job_to_be_done)
                if detected_lang != current_locale and detected_lang in i18n.get_available_locales():
                    i18n.set_locale(detected_lang)
                    session['locale'] = detected_lang
            
            if not persona or not job_to_be_done:
                error_msg = i18n.t('errors.no_persona') if not persona else i18n.t('errors.no_job') if I18N_AVAILABLE else 'Both persona and job-to-be-done are required'
                return jsonify({'error': error_msg}), 400
            
            # Get uploaded files
            files = request.files.getlist('pdf_files') 
            if not files or all(f.filename == '' for f in files):
                error_msg = i18n.t('errors.no_files') if I18N_AVAILABLE else 'No PDF files uploaded'
                return jsonify({'error': error_msg}), 400
            
            # Create demo response with current locale
            current_locale = i18n.current_locale if I18N_AVAILABLE else 'en'
            demo_result = create_demo_response(persona, job_to_be_done, files, current_locale)
            
            return jsonify(demo_result)
            
        except Exception as e:
            error_msg = i18n.t('errors.processing_failed') if I18N_AVAILABLE else f'Demo processing failed: {str(e)}'
            return jsonify({'error': error_msg}), 500
    
    return app

def create_demo_response(persona, job_to_be_done, files, locale='en'):
    """Create a demo response showing the expected output structure"""
    
    # Generate demo metadata
    metadata = {
        "input_documents": [
            {
                "filename": file.filename,
                "pages": 15,  # Demo value
                "has_tables": True,
                "sections_found": 8
            }
            for file in files if file.filename
        ],
        "persona": persona,
        "job_to_be_done": job_to_be_done,
        "timestamp": datetime.now().isoformat(),
        "processing_summary": {
            "total_documents": len([f for f in files if f.filename]),
            "total_sections_analyzed": 25,  # Demo value
            "total_tables_found": 5  # Demo value
        }
    }
    
    # Generate demo extracted sections based on persona
    extracted_sections = generate_demo_sections(persona, job_to_be_done, locale)
    
    # Generate demo subsection analysis
    subsection_analysis = generate_demo_subsections(persona, job_to_be_done, extracted_sections[:5], locale)
    
    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis,
        "processing_time": 2.5,  # Demo value
        "demo_mode": True,
        "note": "This is a demonstration showing the expected output structure. Full functionality requires PDF processing libraries."
    }

def generate_demo_sections(persona, job_to_be_done, locale='en'):
    """Generate demo sections based on persona type"""
    
    # Determine persona type
    persona_lower = persona.lower()
    if 'hr' in persona_lower or 'human' in persona_lower:
        persona_type = 'hr'
    elif 'student' in persona_lower or 'academic' in persona_lower:
        persona_type = 'student'
    elif 'analyst' in persona_lower or 'data' in persona_lower:
        persona_type = 'analyst'
    else:
        persona_type = 'general'
    
    # Persona-specific demo sections
    demo_sections = {
        'hr': [
            {
                "document": "employee_handbook.pdf",
                "page_number": 3,
                "original_section_title": "Employee Onboarding Process",
                "persona_adapted_title": "Streamlined E-Signature Workflow for New Hire Documentation",
                "importance_rank": 1,
                "relevance_scores": {
                    "semantic_similarity": 0.89,
                    "keyword_match": 0.92,
                    "heading_weight": 0.8,
                    "positional_score": 0.9,
                    "content_quality": 0.85,
                    "total_score": 0.87
                },
                "content_preview": "The employee onboarding process involves multiple forms and documentation requirements that can be streamlined through digital workflows...",
                "word_count": 245,
                "has_tables": True
            },
            {
                "document": "compliance_guide.pdf",
                "page_number": 7,
                "original_section_title": "Documentation Requirements",
                "persona_adapted_title": "Onboarding Compliance Forms and Digital Signature Integration",
                "importance_rank": 2,
                "relevance_scores": {
                    "semantic_similarity": 0.82,
                    "keyword_match": 0.88,
                    "heading_weight": 0.75,
                    "positional_score": 0.7,
                    "content_quality": 0.8,
                    "total_score": 0.79
                },
                "content_preview": "All new employees must complete mandatory documentation including tax forms, benefits enrollment, and company policy acknowledgments...",
                "word_count": 189,
                "has_tables": False
            }
        ],
        'student': [
            {
                "document": "study_guide.pdf",
                "page_number": 12,
                "original_section_title": "Key Concepts and Definitions",
                "persona_adapted_title": "Exam-Centric Key Concepts for Academic Success",
                "importance_rank": 1,
                "relevance_scores": {
                    "semantic_similarity": 0.91,
                    "keyword_match": 0.85,
                    "heading_weight": 0.9,
                    "positional_score": 0.8,
                    "content_quality": 0.88,
                    "total_score": 0.87
                },
                "content_preview": "Understanding fundamental concepts is crucial for exam success. This section covers the most important definitions and theories...",
                "word_count": 312,
                "has_tables": True
            },
            {
                "document": "lecture_notes.pdf",
                "page_number": 5,
                "original_section_title": "Practice Problems",
                "persona_adapted_title": "Simplified Study Guides with Worked Examples",
                "importance_rank": 2,
                "relevance_scores": {
                    "semantic_similarity": 0.86,
                    "keyword_match": 0.83,
                    "heading_weight": 0.7,
                    "positional_score": 0.9,
                    "content_quality": 0.75,
                    "total_score": 0.81
                },
                "content_preview": "These practice problems demonstrate the application of key concepts with step-by-step solutions for better understanding...",
                "word_count": 267,
                "has_tables": False
            }
        ],
        'analyst': [
            {
                "document": "market_report.pdf",
                "page_number": 8,
                "original_section_title": "Market Trends Analysis",
                "persona_adapted_title": "Market Trend Visualizations for Strategic Decision Making",
                "importance_rank": 1,
                "relevance_scores": {
                    "semantic_similarity": 0.93,
                    "keyword_match": 0.89,
                    "heading_weight": 0.85,
                    "positional_score": 0.75,
                    "content_quality": 0.92,
                    "total_score": 0.87
                },
                "content_preview": "Current market trends show significant growth in key sectors with implications for investment strategies and business planning...",
                "word_count": 421,
                "has_tables": True
            },
            {
                "document": "financial_data.pdf",
                "page_number": 15,
                "original_section_title": "Investment Performance",
                "persona_adapted_title": "R&D Investment Insights and Performance Analytics",
                "importance_rank": 2,
                "relevance_scores": {
                    "semantic_similarity": 0.88,
                    "keyword_match": 0.91,
                    "heading_weight": 0.8,
                    "positional_score": 0.6,
                    "content_quality": 0.85,
                    "total_score": 0.81
                },
                "content_preview": "Investment performance data reveals patterns in R&D spending effectiveness and potential areas for optimization...",
                "word_count": 356,
                "has_tables": True
            }
        ]
    }
    
    # Get sections for the persona type or use general sections
    sections = demo_sections.get(persona_type, demo_sections['hr'])
    
    # Add more generic sections
    sections.extend([
        {
            "document": "additional_doc.pdf",
            "page_number": 2,
            "original_section_title": "Introduction and Overview",
            "persona_adapted_title": f"Strategic Overview for {persona}",
            "importance_rank": 3,
            "relevance_scores": {
                "semantic_similarity": 0.75,
                "keyword_match": 0.72,
                "heading_weight": 0.9,
                "positional_score": 0.95,
                "content_quality": 0.78,
                "total_score": 0.78
            },
            "content_preview": "This introductory section provides context and background information relevant to the main objectives...",
            "word_count": 198,
            "has_tables": False
        }
    ])
    
    return sections

def generate_demo_subsections(persona, job_to_be_done, top_sections, locale='en'):
    """Generate demo subsection analysis"""
    subsections = []
    
    for i, section in enumerate(top_sections):
        subsection = {
            "document": section["document"],
            "page_number": section["page_number"],
            "section_title": section["original_section_title"],
            "persona_adapted_title": section["persona_adapted_title"],
            "refined_text": f"For {persona}: This section provides crucial insights for {job_to_be_done.lower()}. The content has been analyzed and refined to highlight the most relevant information for your specific needs. Key points include implementation strategies, best practices, and actionable recommendations.",
            "importance_rank": section["importance_rank"],
            "actionable_insights": [
                f"Consider implementing automated workflows to support {job_to_be_done.lower()}",
                f"Focus on user experience optimization for {persona.lower()} requirements",
                "Establish clear metrics and monitoring for continuous improvement"
            ],
            "table_integration": {
                "table_count": 1 if section.get("has_tables") else 0,
                "total_rows": 12 if section.get("has_tables") else 0,
                "table_details": [
                    {
                        "table_index": 1,
                        "rows": 12,
                        "columns": 4,
                        "headers": ["Item", "Description", "Status", "Priority"],
                        "source": "demo_data"
                    }
                ] if section.get("has_tables") else []
            } if section.get("has_tables") else None
        }
        
        subsections.append(subsection)
    
    return subsections

def main():
    """Main function to run the demo application"""
    if not FLASK_AVAILABLE:
        print("Flask is not available. Cannot start web server.")
        print("This is a demo showing the expected system architecture and output structure.")
        return
    
    print("=== Persona-Driven PDF Analysis System (Demo Mode) ===")
    print("Starting demo web server...")
    print("\nNote: This is a demonstration version showing the expected output structure.")
    print("Full functionality requires PDF processing libraries (PyMuPDF, pdfplumber, etc.)")
    
    app = create_demo_app()
    if app:
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Could not create demo application")

if __name__ == "__main__":
    main()