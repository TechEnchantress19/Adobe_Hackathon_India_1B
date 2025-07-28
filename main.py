#!/usr/bin/env python3
"""
Main entry point for the Persona-Driven PDF Analysis System
Supports both CLI and web modes
"""

import argparse
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Attempt to import full dependencies, but allow falling back to demo mode
try:
    from core.pdf_processor import PDFProcessor
    from core.persona_analyzer import PersonaAnalyzer
    from core.ranking_engine import RankingEngine
    from core.output_generator import OutputGenerator
    from app import create_app
    FULL_LIBS_AVAILABLE = True
except ImportError:
    FULL_LIBS_AVAILABLE = False


def cli_mode(args):
    """Run the application in CLI mode"""
    print("=== Persona-Driven PDF Analysis System ===")
    print("CLI Mode\n")

    # Fallback to offline demo if core libraries are missing
    if not FULL_LIBS_AVAILABLE:
        print("Error: Core libraries are missing. Running in offline demo mode.")
        try:
            from cli_offline import main as offline_main
            # In a real scenario, you'd pass args through, but the demo script handles it
            offline_main()
        except ImportError:
            print("Offline demo script (cli_offline.py) not found.")
        return

    # Determine input source
    input_path = Path(args.input) if args.input else None
    output_dir = Path(args.output)
    pdf_files_arg = args.files

    pdf_files = []
    if pdf_files_arg:
        # Specific files provided
        pdf_files = [Path(f) for f in pdf_files_arg if Path(f).suffix.lower() == '.pdf' and Path(f).exists()]
    elif input_path and input_path.is_file() and input_path.suffix.lower() == '.pdf':
        # Single PDF file
        pdf_files = [input_path]
    elif input_path and input_path.is_dir():
        # **MODIFIED LINE: Recursively search for PDFs in the directory**
        print(f"Searching for PDF files in {input_path} and its subdirectories...")
        pdf_files = list(input_path.glob("**/*.pdf"))
    else:
        # Default locations (also recursive)
        default_dirs = [Path("./input"), Path("./sample_pdfs"), Path(".")]
        for dir_path in default_dirs:
            if dir_path.exists():
                pdf_files.extend(dir_path.glob("**/*.pdf"))
                if pdf_files:
                    print(f"Found files in default directory: {dir_path}")
                    break

    if not pdf_files:
        print("Error: No PDF files found.")
        print("Usage options:")
        print("  - Place PDFs in './input' directory (or subdirectories)")
        print("  - Use --input to specify a directory or file")
        print("  - Use --files to specify individual files")
        return

    print(f"Found {len(pdf_files)} PDF files to process:")
    for pdf in pdf_files[:5]: # Print first 5 found
        print(f"  - {pdf}")
    if len(pdf_files) > 5:
        print(f"  ... and {len(pdf_files) - 5} more.")
    print()

    # Get persona and job from user if not provided
    persona = args.persona
    job_to_be_done = args.job

    if not persona:
        print("Please enter the following information:")
        persona = input("Persona (e.g., 'HR professional', 'Student', 'Analyst'): ").strip()

    if not job_to_be_done:
        job_to_be_done = input("Job-to-be-done (e.g., 'Create and manage fillable forms for onboarding'): ").strip()

    if not persona or not job_to_be_done:
        print("Error: Both persona and job-to-be-done are required.")
        return

    print(f"\nProcessing {len(pdf_files)} PDFs for persona: {persona}")
    print(f"Job-to-be-done: {job_to_be_done}\n")

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    start_time = time.time()

    try:
        # Initialize components
        pdf_processor = PDFProcessor()
        persona_analyzer = PersonaAnalyzer()
        ranking_engine = RankingEngine()
        output_generator = OutputGenerator()

        # Process PDFs
        all_documents = []
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}...")
            doc_data = pdf_processor.process_pdf(str(pdf_file))
            doc_data['filename'] = pdf_file.name
            all_documents.append(doc_data)

        # Analyze with persona
        print("Analyzing content with persona context...")
        persona_context = persona_analyzer.analyze_persona(persona, job_to_be_done)

        # Rank sections
        print("Ranking sections by importance...")
        ranked_sections = ranking_engine.rank_sections(all_documents, persona_context)

        # Generate output
        print("Generating output...")
        result = output_generator.generate_output(
            documents=all_documents,
            persona=persona,
            job_to_be_done=job_to_be_done,
            ranked_sections=ranked_sections,
            persona_context=persona_context
        )

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"analysis_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        processing_time = time.time() - start_time
        print(f"\nProcessing completed in {processing_time:.2f} seconds")
        print(f"Results saved to: {output_file}")
        print(f"Found {len(ranked_sections)} relevant sections")

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        sys.exit(1)


def web_mode(port=8000):
    """Run the application in web mode"""
    app = create_app() if FULL_LIBS_AVAILABLE else None
    if not app:
        print("Error: Core libraries are missing. Cannot start web server.")
        print("Please install dependencies from requirements.txt")
        return

    print("=== Persona-Driven PDF Analysis System ===")
    print(f"Starting web server on http://0.0.0.0:{port}...")
    app.run(host='0.0.0.0', port=port, debug=False)


def main():
    parser = argparse.ArgumentParser(description='Persona-Driven PDF Analysis System')
    parser.add_argument('--cli', action='store_true', help='Run in command-line mode')
    parser.add_argument('--web', action='store_true', help='Run in web mode')
    parser.add_argument('--port', type=int, default=8000, help='Port for web mode (default: 8000)')

    # Arguments specific to CLI mode
    parser.add_argument('--input', '-i', type=str, default='./input', help='Input directory or single PDF file for CLI')
    parser.add_argument('--files', '-f', nargs='+', help='Specific PDF files to process for CLI')
    parser.add_argument('--output', '-o', type=str, default='./output', help='Output directory for results (default: ./output)')
    parser.add_argument('--persona', '-p', type=str, help='Your persona/role (e.g., "HR Professional")')
    parser.add_argument('--job', '-j', type=str, help='Your job-to-be-done')

    args = parser.parse_args()

    if args.cli:
        cli_mode(args)
    elif args.web:
        web_mode(args.port)
    else:
        # Default to web mode if no other mode is specified
        print("No mode specified, defaulting to --web")
        web_mode(args.port)


if __name__ == "__main__":
    main()