"""
Advanced table extraction and processing utilities
"""

import pandas as pd
import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np


class TableExtractor:
    """Advanced table extraction and analysis utilities"""
    
    def __init__(self):
        self.numeric_patterns = [
            r'^\$?[\d,]+\.?\d*$',  # Currency and numbers
            r'^\d+%$',             # Percentages
            r'^\d{4}$',            # Years
            r'^[\d\.,]+$'          # General numeric
        ]
    
    def process_raw_table(self, table_data: List[List[str]], source: str = 'unknown') -> Dict[str, Any] | None:
        """Process raw table data into structured format"""
        if not table_data or len(table_data) < 2:
            return None
        
        # Extract headers and data
        headers = table_data[0]
        data_rows = table_data[1:]
        
        # Clean headers
        clean_headers = [self._clean_cell_content(header) for header in headers]
        
        # Process data rows
        processed_rows = []
        for row in data_rows:
            if len(row) == len(headers):  # Ensure row completeness
                clean_row = [self._clean_cell_content(cell) for cell in row]
                processed_rows.append(clean_row)
        
        if not processed_rows:
            return None
        
        # Create DataFrame for analysis
        try:
            df = pd.DataFrame(processed_rows, columns=clean_headers)
            
            # Analyze table structure
            analysis = self._analyze_table_structure(df)
            
            return {
                'headers': clean_headers,
                'data': processed_rows,
                'row_count': len(processed_rows),
                'column_count': len(clean_headers),
                'source': source,
                'analysis': analysis,
                'dataframe': df
            }
        
        except Exception as e:
            print(f"Error processing table: {e}")
            return {
                'headers': clean_headers,
                'data': processed_rows,
                'row_count': len(processed_rows),
                'column_count': len(clean_headers),
                'source': source,
                'error': str(e)
            }
    
    def _clean_cell_content(self, cell: str) -> str:
        """Clean individual cell content"""
        if not isinstance(cell, str):
            return str(cell) if cell is not None else ""
        
        # Remove extra whitespace
        cell = re.sub(r'\s+', ' ', cell.strip())
        
        # Remove common PDF artifacts
        cell = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cell)  # Control characters
        
        # Fix encoding issues
        cell = cell.replace('\ufeff', '')  # BOM
        cell = cell.replace('\u2013', '-')  # En dash
        cell = cell.replace('\u2014', '--')  # Em dash
        cell = cell.replace('\u2019', "'")  # Right single quotation mark
        
        return cell
    
    def _analyze_table_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze table structure and content types"""
        analysis = {
            'column_types': {},
            'numeric_columns': [],
            'text_columns': [],
            'date_columns': [],
            'empty_cells': 0,
            'completeness': 0
        }
        
        total_cells = df.shape[0] * df.shape[1]
        empty_cells = 0
        
        for column in df.columns:
            col_data = df[column].astype(str)
            
            # Count empty cells
            empty_in_col = sum(1 for val in col_data if not val or val.strip() == '')
            empty_cells += empty_in_col
            
            # Determine column type
            col_type = self._determine_column_type(col_data)
            analysis['column_types'][column] = col_type
            
            # Categorize columns
            if col_type == 'numeric':
                analysis['numeric_columns'].append(column)
            elif col_type == 'date':
                analysis['date_columns'].append(column)
            else:
                analysis['text_columns'].append(column)
        
        analysis['empty_cells'] = empty_cells
        analysis['completeness'] = round((total_cells - empty_cells) / total_cells * 100, 1) if total_cells > 0 else 0
        
        return analysis
    
    def _determine_column_type(self, column_data: pd.Series) -> str:
        """Determine the data type of a column"""
        non_empty_values = [val for val in column_data if val and val.strip()]
        
        if not non_empty_values:
            return 'empty'
        
        # Check for numeric data
        numeric_count = 0
        date_count = 0
        
        for value in non_empty_values[:10]:  # Sample first 10 values
            value = value.strip()
            
            # Check if numeric
            if any(re.match(pattern, value) for pattern in self.numeric_patterns):
                numeric_count += 1
            
            # Check if date-like
            elif self._is_date_like(value):
                date_count += 1
        
        sample_size = min(10, len(non_empty_values))
        
        if numeric_count >= sample_size * 0.7:
            return 'numeric'
        elif date_count >= sample_size * 0.7:
            return 'date'
        else:
            return 'text'
    
    def _is_date_like(self, value: str) -> bool:
        """Check if a value looks like a date"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',      # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',      # MM-DD-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',        # YYYY-MM-DD
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',  # DD Mon
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}',  # Mon DD
        ]
        
        return any(re.search(pattern, value, re.IGNORECASE) for pattern in date_patterns)
    
    def extract_table_insights(self, table: Dict[str, Any], persona_context: Dict[str, Any]) -> List[str]:
        """Extract persona-specific insights from table data"""
        insights = []
        
        if not table or 'analysis' not in table:
            return insights
        
        analysis = table['analysis']
        row_count = table.get('row_count', 0)
        column_count = table.get('column_count', 0)
        
        # Basic table characteristics
        if row_count > 20:
            insights.append(f"Large dataset with {row_count} rows - consider pagination or filtering for user interface")
        
        # Completeness insights
        completeness = analysis.get('completeness', 0)
        if completeness < 80:
            insights.append(f"Data completeness is {completeness}% - may need data validation or cleanup")
        
        # Column type insights
        numeric_cols = analysis.get('numeric_columns', [])
        if numeric_cols:
            insights.append(f"Contains {len(numeric_cols)} numeric columns suitable for calculations and analysis")
        
        # Persona-specific insights
        persona_type = persona_context.get('persona_type', 'general')
        
        if persona_type == 'hr':
            if any('employee' in col.lower() or 'name' in col.lower() for col in table.get('headers', [])):
                insights.append("Employee data detected - ensure GDPR/privacy compliance for form design")
            
            if any('date' in col.lower() for col in table.get('headers', [])):
                insights.append("Date fields present - consider automated date validation in forms")
        
        elif persona_type == 'analyst':
            if len(numeric_cols) > 1:
                insights.append("Multiple numeric columns available for correlation analysis and visualization")
            
            if row_count > 10:
                insights.append("Sufficient data volume for statistical analysis and trend identification")
        
        elif persona_type == 'student':
            insights.append("Table data can be used for practice exercises and case study analysis")
            
            if any('score' in col.lower() or 'grade' in col.lower() for col in table.get('headers', [])):
                insights.append("Performance data available for academic progress tracking")
        
        return insights[:3]  # Limit to top 3 insights
    
    def convert_to_summary(self, table: Dict[str, Any], max_rows: int = 5) -> Dict[str, Any] | None:
        """Convert table to summary format for display"""
        if not table:
            return None
        
        headers = table.get('headers', [])
        data = table.get('data', [])
        
        # Limit data for summary
        summary_data = data[:max_rows] if len(data) > max_rows else data
        
        summary = {
            'headers': headers,
            'sample_data': summary_data,
            'total_rows': len(data),
            'total_columns': len(headers),
            'showing_rows': len(summary_data),
            'analysis': table.get('analysis', {}),
            'truncated': len(data) > max_rows
        }
        
        return summary
    
    def merge_similar_tables(self, tables: List[Dict[str, Any]], similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Merge tables with similar structure"""
        if len(tables) <= 1:
            return tables
        
        merged_tables = []
        processed_indices = set()
        
        for i, table1 in enumerate(tables):
            if i in processed_indices:
                continue
            
            similar_tables = [table1]
            processed_indices.add(i)
            
            for j, table2 in enumerate(tables[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                # Check header similarity
                headers1 = set(table1.get('headers', []))
                headers2 = set(table2.get('headers', []))
                
                if headers1 and headers2:
                    similarity = len(headers1 & headers2) / len(headers1 | headers2)
                    
                    if similarity >= similarity_threshold:
                        similar_tables.append(table2)
                        processed_indices.add(j)
            
            # If multiple similar tables found, merge them
            if len(similar_tables) > 1:
                merged_table = self._merge_table_group(similar_tables)
                merged_tables.append(merged_table)
            else:
                merged_tables.append(table1)
        
        return merged_tables
    
    def _merge_table_group(self, tables: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        """Merge a group of similar tables"""
        if not tables:
            return None
        
        # Use headers from the first table
        merged_headers = tables[0].get('headers', [])
        merged_data = []
        
        # Combine data from all tables
        for table in tables:
            table_data = table.get('data', [])
            merged_data.extend(table_data)
        
        # Create merged table
        merged_table = {
            'headers': merged_headers,
            'data': merged_data,
            'row_count': len(merged_data),
            'column_count': len(merged_headers),
            'source': f"merged_from_{len(tables)}_tables",
            'original_table_count': len(tables)
        }
        
        # Re-analyze merged table
        if merged_data:
            try:
                df = pd.DataFrame(merged_data, columns=merged_headers)
                merged_table['analysis'] = self._analyze_table_structure(df)
            except Exception as e:
                merged_table['analysis'] = {'error': str(e)}
        
        return merged_table
