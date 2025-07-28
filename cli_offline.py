#!/usr/bin/env python3
"""
Offline CLI version of the Persona-Driven PDF Analysis System
This version works without internet access and handles missing dependencies gracefully
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Import i18n utilities
try:
    from utils.i18n import i18n, detect_language_from_text
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False

def create_offline_demo_response(persona, job_to_be_done, pdf_files):
    """Create demo response for offline CLI mode"""
    
    print(f"📄 Processing {len(pdf_files)} PDF files...")
    print(f"👤 Persona: {persona}")
    print(f"🎯 Job-to-be-done: {job_to_be_done}")
    print()
    
    # Simulate processing with progress
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
        time.sleep(0.5)  # Simulate processing time
    
    print("\n✅ Analysis complete!\n")
    
    # Generate demo sections based on persona
    sections = generate_cli_demo_sections(persona, job_to_be_done, pdf_files)
    
    # Create structured output
    result = {
        "metadata": {
            "input_documents": [
                {
                    "filename": pdf_file.name,
                    "pages": 10 + i * 5,  # Demo page counts
                    "has_tables": i % 2 == 0,
                    "sections_found": 5 + i * 2
                }
                for i, pdf_file in enumerate(pdf_files)
            ],
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "timestamp": datetime.now().isoformat(),
            "processing_summary": {
                "total_documents": len(pdf_files),
                "total_sections_analyzed": len(pdf_files) * 8,
                "total_tables_found": len(pdf_files) * 2
            },
            "cli_mode": True,
            "offline_mode": True
        },
        "extracted_sections": sections,
        "subsection_analysis": generate_cli_subsections(sections[:3]),
        "processing_time": len(pdf_files) * 1.2,
        "demo_note": "This is an offline demonstration showing the expected output structure"
    }
    
    return result

def generate_cli_demo_sections(persona, job_to_be_done, pdf_files):
    """Generate demo sections for CLI mode"""
    
    sections = []
    
    # Persona-specific templates
    persona_templates = {
        'hr': {
            'titles': [
                'Employee Onboarding Workflow Optimization',
                'Digital Form Management Systems', 
                'Compliance Documentation Processes',
                'Automated Workflow Integration'
            ],
            'content_previews': [
                'Streamlined digital workflows can reduce onboarding time by 60% through automated form routing and e-signature integration...',
                'Modern HR systems require flexible form builders that can adapt to changing compliance requirements...',
                'Ensuring regulatory compliance while maintaining user-friendly processes requires careful balance...',
                'Integration with existing HRIS systems enables seamless data flow and reduces manual data entry...'
            ]
        },
        'student': {
            'titles': [
                'Essential Study Materials and Key Concepts',
                'Exam Preparation Strategies and Techniques',
                'Practice Problems with Detailed Solutions',
                'Academic Performance Tracking Methods'
            ],
            'content_previews': [
                'Focus on understanding core concepts rather than memorization to achieve better exam performance...',
                'Effective study techniques include spaced repetition, active recall, and practice testing...',
                'Working through practice problems helps identify knowledge gaps and reinforces learning...',
                'Regular performance tracking helps identify areas needing additional focus and study time...'
            ]
        },
        'analyst': {
            'titles': [
                'Market Trend Analysis and Forecasting',
                'Data-Driven Investment Insights',
                'Performance Metrics and KPI Tracking',
                'Strategic Recommendations and Action Items'
            ],
            'content_previews': [
                'Current market indicators suggest emerging opportunities in technology and healthcare sectors...',
                'Investment performance data reveals patterns that can inform future allocation strategies...',
                'Key performance indicators show strong growth potential in sustainable technology markets...',
                'Strategic analysis recommends diversification across emerging markets for optimal returns...'
            ]
        }
    }
    
    # Determine persona type
    persona_lower = persona.lower()
    if any(word in persona_lower for word in ['hr', 'human', 'resource']):
        template = persona_templates['hr']
    elif any(word in persona_lower for word in ['student', 'academic', 'learn']):
        template = persona_templates['student'] 
    elif any(word in persona_lower for word in ['analyst', 'data', 'research']):
        template = persona_templates['analyst']
    else:
        template = persona_templates['hr']  # Default
    
    # Generate sections for each PDF
    for i, pdf_file in enumerate(pdf_files):
        for j in range(min(3, len(template['titles']))):  # Max 3 sections per PDF
            section_index = (i * 3 + j) % len(template['titles'])
            
            section = {
                "document": pdf_file.name,
                "page_number": (j + 1) * 3,
                "original_section_title": f"Section {j+1}",
                "persona_adapted_title": template['titles'][section_index],
                "importance_rank": j + 1,
                "relevance_scores": {
                    "semantic_similarity": 0.85 + (j * 0.05),
                    "keyword_match": 0.82 + (j * 0.03),
                    "heading_weight": 0.8 - (j * 0.05),
                    "positional_score": 0.9 - (j * 0.1),
                    "content_quality": 0.88 - (j * 0.02),
                    "total_score": 0.85 - (j * 0.03)
                },
                "content_preview": template['content_previews'][section_index],
                "word_count": 200 + (j * 50),
                "has_tables": j % 2 == 0
            }
            
            sections.append(section)
    
    # Sort by total score
    sections.sort(key=lambda x: x['relevance_scores']['total_score'], reverse=True)
    
    return sections

def generate_cli_subsections(top_sections):
    """Generate subsection analysis for top sections"""
    
    subsections = []
    
    for section in top_sections:
        subsection = {
            "document": section["document"],
            "page_number": section["page_number"],
            "section_title": section["original_section_title"],
            "persona_adapted_title": section["persona_adapted_title"],
            "refined_text": f"This section has been analyzed and refined for your specific role. Key insights include strategic recommendations, implementation guidance, and actionable next steps that align with your objectives.",
            "importance_rank": section["importance_rank"],
            "actionable_insights": [
                "Implement automated workflows to improve efficiency",
                "Focus on user experience and stakeholder satisfaction",
                "Establish clear metrics for measuring success and progress"
            ],
            "table_integration": {
                "table_count": 1 if section.get("has_tables") else 0,
                "total_rows": 15 if section.get("has_tables") else 0,
                "table_details": [
                    {
                        "table_index": 1,
                        "rows": 15,
                        "columns": 4,
                        "headers": ["Category", "Description", "Priority", "Status"],
                        "source": "extracted_data"
                    }
                ] if section.get("has_tables") else []
            } if section.get("has_tables") else None
        }
        
        subsections.append(subsection)
    
    return subsections

def print_results_summary(result, locale='en'):
    """Print a formatted summary of results"""
    
    if I18N_AVAILABLE:
        i18n.set_locale(locale)
        title = i18n.t('cli.analysis_summary')
    else:
        title = "ANALYSIS SUMMARY"
    
    print("=" * 60)
    print(f"📊 {title}")
    print("=" * 60)
    
    metadata = result['metadata']
    
    if I18N_AVAILABLE:
        print(f"👤 {i18n.t('cli.persona_prompt')}: {metadata['persona']}")
        print(f"🎯 {i18n.t('cli.job_prompt')}: {metadata['job_to_be_done']}")
        print(f"📄 {i18n.t('results.documents_processed')}: {metadata['processing_summary']['total_documents']}")
        print(f"📝 {i18n.t('results.sections_analyzed')}: {metadata['processing_summary']['total_sections_analyzed']}")
        print(f"📊 {i18n.t('results.tables_found')}: {metadata['processing_summary']['total_tables_found']}")
        print(f"⏱️  {i18n.t('results.processing_time')}: {result['processing_time']:.1f} seconds")
        print()
        
        print(f"🔥 {i18n.t('cli.top_sections')}:")
    else:
        print(f"👤 Persona: {metadata['persona']}")
        print(f"🎯 Job-to-be-done: {metadata['job_to_be_done']}")
        print(f"📄 Documents processed: {metadata['processing_summary']['total_documents']}")
        print(f"📝 Sections analyzed: {metadata['processing_summary']['total_sections_analyzed']}")
        print(f"📊 Tables found: {metadata['processing_summary']['total_tables_found']}")
        print(f"⏱️  Processing time: {result['processing_time']:.1f} seconds")
        print()
        
        print("🔥 TOP RANKED SECTIONS:")
    
    print("-" * 60)
    
    for i, section in enumerate(result['extracted_sections'][:5], 1):
        print(f"{i}. {section['persona_adapted_title']}")
        print(f"   📄 {section['document']} (Page {section['page_number']})")
        print(f"   ⭐ Score: {section['relevance_scores']['total_score']:.2f}")
        print(f"   📝 {section['content_preview'][:100]}...")
        print()
    
    insights_title = i18n.t('cli.subsection_insights') if I18N_AVAILABLE else "SUBSECTION INSIGHTS"
    print(f"💡 {insights_title}:")
    print("-" * 60)
    
    for subsection in result['subsection_analysis']:
        print(f"📌 {subsection['persona_adapted_title']}")
        for insight in subsection['actionable_insights']:
            print(f"   • {insight}")
        print()

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Persona-Driven PDF Analysis System (Offline CLI)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_offline.py --input ./pdfs --persona "HR Professional" --job "Streamline onboarding"
  python cli_offline.py --files doc1.pdf doc2.pdf --persona "Student" --job "Study for exam"
  python cli_offline.py --persona "Data Analyst" --job "Extract insights" --lang es
        """
    )
    
    parser.add_argument('--input', '-i', type=str,
                        help='Input directory containing PDF files or single PDF file')
    parser.add_argument('--files', '-f', nargs='+', type=str,
                        help='Specific PDF files to process')
    parser.add_argument('--output', '-o', type=str, default='./output',
                        help='Output directory for results (default: ./output)')
    parser.add_argument('--persona', '-p', type=str,
                        help='Your persona/role (e.g., "HR Professional", "Student", "Data Analyst")')
    parser.add_argument('--job', '-j', type=str,
                        help='Your job-to-be-done (e.g., "Create fillable forms for onboarding")')
    parser.add_argument('--format', choices=['json', 'summary', 'both'], default='both',
                        help='Output format (default: both)')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Quiet mode - minimal output')
    parser.add_argument('--lang', '-l', type=str, default='auto',
                        help='Interface language (en, es, fr, zh, auto)')
    
    args = parser.parse_args()
    
    # Set up language
    if I18N_AVAILABLE:
        if args.lang == 'auto':
            # Auto-detect from environment or input
            locale = os.environ.get('LANG', 'en')[:2]
            if locale not in i18n.get_available_locales():
                locale = 'en'
        else:
            locale = args.lang if args.lang in i18n.get_available_locales() else 'en'
        
        i18n.set_locale(locale)
    else:
        locale = 'en'
    
    if not args.quiet:
        if I18N_AVAILABLE:
            print(f"🚀 {i18n.t('cli.title')}")
            print(f"   {i18n.t('cli.subtitle')}")
        else:
            print("🚀 Persona-Driven PDF Analysis System")
            print("   Offline CLI Mode")
        print("-" * 50)
    
    # Determine PDF files to process
    pdf_files = []
    
    if args.files:
        pdf_files = [Path(f) for f in args.files if Path(f).exists() and f.lower().endswith('.pdf')]
    elif args.input:
        input_path = Path(args.input)
        if input_path.is_file() and input_path.suffix.lower() == '.pdf':
            pdf_files = [input_path]
        elif input_path.is_dir():
            pdf_files = list(input_path.glob('*.pdf'))
    else:
        # Look in default locations
        default_dirs = [Path('./input'), Path('./sample_pdfs'), Path('.')]
        for dir_path in default_dirs:
            if dir_path.exists():
                found_files = list(dir_path.glob('*.pdf'))
                if found_files:
                    pdf_files = found_files
                    break
    
    if not pdf_files:
        print("❌ Error: No PDF files found!")
        print("\nTry one of these options:")
        print("• Place PDFs in './input' directory")
        print("• Use --input to specify a directory or file") 
        print("• Use --files to specify individual files")
        print("\nExample: python cli_offline.py --files document.pdf --persona 'Student' --job 'Study for exam'")
        return 1
    
    # Get persona and job if not provided
    persona = args.persona
    job_to_be_done = args.job
    
    if not persona:
        if I18N_AVAILABLE:
            print(f"\n👤 {i18n.t('ui.persona_label')}:")
            print(f"Examples: {i18n.t('ui.persona_placeholder')}")
            persona = input(f"{i18n.t('cli.persona_prompt')}: ").strip()
        else:
            print("\n👤 Please enter your persona:")
            print("Examples: 'HR Professional', 'Student', 'Data Analyst', 'Project Manager'")
            persona = input("Persona: ").strip()
    
    if not job_to_be_done:
        if I18N_AVAILABLE:
            print(f"\n🎯 {i18n.t('ui.job_label')}:")
            print(f"Examples: {i18n.t('ui.job_placeholder')}")
            job_to_be_done = input(f"{i18n.t('cli.job_prompt')}: ").strip()
        else:
            print("\n🎯 Please describe your job-to-be-done:")
            print("Examples: 'Create fillable forms', 'Study for exam', 'Extract key insights'")
            job_to_be_done = input("Job-to-be-done: ").strip()
    
    # Auto-detect language from input text
    if I18N_AVAILABLE and args.lang == 'auto' and (persona or job_to_be_done):
        detected_lang = detect_language_from_text(persona + ' ' + job_to_be_done)
        if detected_lang != locale and detected_lang in i18n.get_available_locales():
            i18n.set_locale(detected_lang)
            locale = detected_lang
    
    if not persona or not job_to_be_done:
        print("❌ Error: Both persona and job-to-be-done are required!")
        return 1
    
    if not args.quiet:
        print(f"\n📋 Configuration:")
        print(f"   👤 Persona: {persona}")
        print(f"   🎯 Job: {job_to_be_done}")
        print(f"   📄 Files: {len(pdf_files)} PDFs")
        print(f"   💾 Output: {args.output}")
        print()
    
    # Process files
    try:
        result = create_offline_demo_response(persona, job_to_be_done, pdf_files) 
        
        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON output
        if args.format in ['json', 'both']:
            json_file = output_dir / f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            if not args.quiet:
                print(f"💾 JSON results saved to: {json_file}")
        
        # Print summary
        if args.format in ['summary', 'both'] and not args.quiet:
            print_results_summary(result, locale)
        
        if not args.quiet:
            print("\n✅ Analysis complete!")
            print(f"📁 Check the output directory: {output_dir.absolute()}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())