"""
Flask web application for persona-driven PDF analysis
"""

import os
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file

from core.pdf_processor import PDFProcessor
from core.persona_analyzer import PersonaAnalyzer
from core.ranking_engine import RankingEngine
from core.output_generator import OutputGenerator


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
    
    # Initialize processors
    pdf_processor = PDFProcessor()
    persona_analyzer = PersonaAnalyzer()
    ranking_engine = RankingEngine()
    output_generator = OutputGenerator()
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/analyze', methods=['POST'])
    def analyze_pdfs():
        try:
            # Get form data
            persona = request.form.get('persona', '').strip()
            job_to_be_done = request.form.get('job_to_be_done', '').strip()
            
            if not persona or not job_to_be_done:
                return jsonify({'error': 'Both persona and job-to-be-done are required'}), 400
            
            # Get uploaded files
            files = request.files.getlist('pdf_files')
            if not files or all(f.filename == '' for f in files):
                return jsonify({'error': 'No PDF files uploaded'}), 400
            
            # Validate file types
            pdf_files = []
            for file in files:
                if file and file.filename and file.filename.lower().endswith('.pdf'):
                    pdf_files.append(file)
            
            if not pdf_files:
                return jsonify({'error': 'No valid PDF files found'}), 400
            
            start_time = time.time()
            
            # Process uploaded PDFs
            all_documents = []
            temp_files = []
            
            try:
                for pdf_file in pdf_files:
                    # Save uploaded file temporarily
                    filename = secure_filename(pdf_file.filename)
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    pdf_file.save(temp_path)
                    temp_files.append(temp_path)
                    
                    # Process PDF
                    doc_data = pdf_processor.process_pdf(temp_path)
                    doc_data['filename'] = filename
                    all_documents.append(doc_data)
                
                # Analyze with persona
                persona_context = persona_analyzer.analyze_persona(persona, job_to_be_done)
                
                # Rank sections
                ranked_sections = ranking_engine.rank_sections(all_documents, persona_context)
                
                # Generate output
                result = output_generator.generate_output(
                    documents=all_documents,
                    persona=persona,
                    job_to_be_done=job_to_be_done,
                    ranked_sections=ranked_sections,
                    persona_context=persona_context
                )
                
                processing_time = time.time() - start_time
                result['processing_time'] = round(processing_time, 2)
                
                return jsonify(result)
                
            finally:
                # Clean up temporary files
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        
        except Exception as e:
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    
    @app.route('/download/<filename>')
    def download_result(filename):
        """Download analysis results as JSON file"""
        try:
            # In a real implementation, you'd store results temporarily
            # For now, return error as we don't persist results
            return jsonify({'error': 'Download not available'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
