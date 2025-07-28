"""
PDF processing module for extracting text, headings, tables, and structure
Combines Round 1A functionality with enhanced extraction capabilities
"""

import fitz  # PyMuPDF
import pdfplumber
import camelot
import re
import pandas as pd
from typing import Dict, List, Any, Optional


class PDFProcessor:
    """Processes PDF files to extract text, headings, tables, and structure"""
    
    def __init__(self):
        self.heading_patterns = [
            r'^[A-Z][A-Z\s]{10,}$',  # ALL CAPS headings
            r'^\d+\.?\s+[A-Z]',      # Numbered headings
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*:?\s*$',  # Title case
            r'^[•\-\*]\s*[A-Z]',     # Bullet points
        ]
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a single PDF file and extract all relevant information
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            doc_data = {
                'filename': pdf_path.split('/')[-1],
                'pages': [],
                'headings': [],
                'tables': [],
                'full_text': '',
                'outline': [],
                'metadata': {}
            }
            
            # Extract with PyMuPDF
            pymupdf_data = self._extract_with_pymupdf(pdf_path)
            doc_data.update(pymupdf_data)
            
            # Extract with pdfplumber for enhanced text and tables
            pdfplumber_data = self._extract_with_pdfplumber(pdf_path)
            doc_data['tables'].extend(pdfplumber_data.get('tables', []))
            
            # Extract tables with camelot
            camelot_tables = self._extract_with_camelot(pdf_path)
            doc_data['tables'].extend(camelot_tables)
            
            # Process and enhance headings
            doc_data['headings'] = self._process_headings(doc_data['pages'])
            
            # Generate sections based on headings and content
            doc_data['sections'] = self._generate_sections(doc_data)
            
            return doc_data
            
        except Exception as e:
            return {
                'filename': pdf_path.split('/')[-1],
                'error': f"Failed to process PDF: {str(e)}",
                'pages': [],
                'headings': [],
                'tables': [],
                'sections': []
            }
    
    def _extract_with_pymupdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text, outline, and metadata using PyMuPDF"""
        data = {
            'pages': [],
            'outline': [],
            'metadata': {},
            'full_text': ''
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            # Extract metadata
            data['metadata'] = doc.metadata
            
            # Extract outline/bookmarks
            outline = doc.get_toc()
            for item in outline:
                level, title, page = item
                data['outline'].append({
                    'level': level,
                    'title': title,
                    'page': page
                })
            
            # Extract text from each page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Get text blocks with formatting info
                blocks = page.get_text("dict")
                page_text = page.get_text()
                
                page_data = {
                    'page_number': page_num + 1,
                    'text': page_text,
                    'blocks': self._process_text_blocks(blocks),
                    'bbox': page.rect
                }
                
                data['pages'].append(page_data)
                data['full_text'] += page_text + '\n'
            
            doc.close()
            
        except Exception as e:
            print(f"PyMuPDF extraction error: {e}")
        
        return data
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extract enhanced text and tables using pdfplumber"""
        data = {'tables': []}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:  # Has header and data
                            df = pd.DataFrame(table[1:], columns=table[0])
                            data['tables'].append({
                                'page': page_num + 1,
                                'table_index': table_idx,
                                'data': df.to_dict('records'),
                                'headers': table[0],
                                'source': 'pdfplumber'
                            })
        
        except Exception as e:
            print(f"pdfplumber extraction error: {e}")
        
        return data
    
    def _extract_with_camelot(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables using camelot"""
        tables = []
        
        try:
            # Try lattice method first
            camelot_tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='all')
            
            for table in camelot_tables:
                if table.df is not None and not table.df.empty:
                    tables.append({
                        'page': table.page,
                        'data': table.df.to_dict('records'),
                        'headers': table.df.columns.tolist(),
                        'source': 'camelot_lattice',
                        'accuracy': getattr(table, 'accuracy', 0)
                    })
            
            # Try stream method if lattice didn't find tables
            if not tables:
                camelot_tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
                
                for table in camelot_tables:
                    if table.df is not None and not table.df.empty:
                        tables.append({
                            'page': table.page,
                            'data': table.df.to_dict('records'),
                            'headers': table.df.columns.tolist(),
                            'source': 'camelot_stream',
                            'accuracy': getattr(table, 'accuracy', 0)
                        })
        
        except Exception as e:
            print(f"Camelot extraction error: {e}")
        
        return tables
    
    def _process_text_blocks(self, blocks_dict: Dict) -> List[Dict[str, Any]]:
        """Process text blocks to identify formatting and structure"""
        processed_blocks = []
        
        for block in blocks_dict.get('blocks', []):
            if 'lines' in block:
                for line in block['lines']:
                    for span in line.get('spans', []):
                        text = span.get('text', '').strip()
                        if text:
                            processed_blocks.append({
                                'text': text,
                                'font': span.get('font', ''),
                                'size': span.get('size', 0),
                                'flags': span.get('flags', 0),
                                'bbox': span.get('bbox', []),
                                'is_bold': bool(span.get('flags', 0) & 16),
                                'is_italic': bool(span.get('flags', 0) & 2)
                            })
        
        return processed_blocks
    
    def _process_headings(self, pages: List[Dict]) -> List[Dict[str, Any]]:
        """Identify and process headings from text blocks"""
        headings = []
        
        for page in pages:
            page_num = page['page_number']
            blocks = page.get('blocks', [])
            
            # Find potential headings based on formatting
            for block in blocks:
                text = block['text'].strip()
                if not text:
                    continue
                
                # Check if it's a heading based on various criteria
                is_heading = (
                    block.get('is_bold', False) or
                    block.get('size', 0) > 12 or
                    any(re.match(pattern, text) for pattern in self.heading_patterns) or
                    len(text.split()) <= 8  # Short lines are often headings
                )
                
                if is_heading and len(text) > 5:  # Minimum length for heading
                    level = self._determine_heading_level(block, text)
                    headings.append({
                        'text': text,
                        'page': page_num,
                        'level': level,
                        'font_size': block.get('size', 0),
                        'is_bold': block.get('is_bold', False),
                        'bbox': block.get('bbox', [])
                    })
        
        return headings
    
    def _determine_heading_level(self, block: Dict, text: str) -> int:
        """Determine the hierarchical level of a heading"""
        font_size = block.get('size', 0)
        is_bold = block.get('is_bold', False)
        
        # Rule-based level determination
        if font_size > 16 or (is_bold and font_size > 14):
            return 1  # H1
        elif font_size > 13 or is_bold:
            return 2  # H2
        else:
            return 3  # H3
    
    def _generate_sections(self, doc_data: Dict) -> List[Dict[str, Any]]:
        """Generate sections based on headings and content structure"""
        sections = []
        pages = doc_data['pages']
        headings = doc_data['headings']
        
        if not headings:
            # If no headings found, create sections based on pages
            for page in pages:
                if page['text'].strip():
                    sections.append({
                        'title': f"Page {page['page_number']} Content",
                        'content': page['text'][:500] + "..." if len(page['text']) > 500 else page['text'],
                        'page': page['page_number'],
                        'level': 1,
                        'word_count': len(page['text'].split()),
                        'has_tables': any(t['page'] == page['page_number'] for t in doc_data['tables'])
                    })
            return sections
        
        # Create sections based on headings
        for i, heading in enumerate(headings):
            # Find content between this heading and the next
            current_page = heading['page']
            next_heading = headings[i + 1] if i + 1 < len(headings) else None
            
            # Collect content
            content_parts = []
            
            # Get text from current page starting after heading
            current_page_data = next((p for p in pages if p['page_number'] == current_page), None)
            if current_page_data:
                page_text = current_page_data['text']
                heading_pos = page_text.find(heading['text'])
                if heading_pos >= 0:
                    content_after_heading = page_text[heading_pos + len(heading['text']):]
                    content_parts.append(content_after_heading)
            
            # If next heading is on a different page, include intermediate pages
            if next_heading and next_heading['page'] > current_page:
                for page_num in range(current_page + 1, next_heading['page']):
                    page_data = next((p for p in pages if p['page_number'] == page_num), None)
                    if page_data:
                        content_parts.append(page_data['text'])
            
            # Combine content
            full_content = '\n'.join(content_parts).strip()
            
            # Truncate if too long (keep first 1000 characters for summary)
            content_preview = full_content[:1000] + "..." if len(full_content) > 1000 else full_content
            
            sections.append({
                'title': heading['text'],
                'content': content_preview,
                'page': heading['page'],
                'level': heading['level'],
                'word_count': len(full_content.split()),
                'has_tables': any(
                    current_page <= t['page'] <= (next_heading['page'] if next_heading else current_page)
                    for t in doc_data['tables']
                )
            })
        
        return sections
