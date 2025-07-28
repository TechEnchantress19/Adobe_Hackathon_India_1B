# Persona-Driven PDF Analysis System - CLI Guide

## Overview

This system analyzes PDF documents and extracts relevant sections based on your persona and job-to-be-done, providing ranked results with adaptive headings tailored to your specific context.

## Quick Start

### Option 1: Interactive Mode (Easiest)

```bash
# Linux/Mac
./run_cli.sh

# Windows
run_cli.bat

# Or directly with Python
python cli_offline.py
```

### Option 2: Command Line Arguments

```bash
python cli_offline.py --persona "HR Professional" --job "Streamline employee onboarding" --input ./pdfs
```

## Installation Options

### 1. Standalone (No Dependencies)
The `cli_offline.py` script works without any external dependencies and provides demo functionality showing the expected output structure.

### 2. Full Functionality (Requires Dependencies)
For full PDF processing capabilities, install:

```bash
pip install PyMuPDF pdfplumber pandas numpy scikit-learn sentence-transformers
```

### 3. Docker (Recommended for Production)

```bash
# Build and run web interface
docker-compose up

# Run CLI mode
docker-compose --profile cli up pdf-analysis-cli
```

## Usage Examples

### Basic Usage
```bash
# Interactive mode - will prompt for persona and job
python cli_offline.py --input ./documents

# Specify everything via command line
python cli_offline.py \
  --input ./reports \
  --persona "Data Analyst" \
  --job "Extract quarterly performance metrics" \
  --output ./analysis_results
```

### Multiple Files
```bash
python cli_offline.py \
  --files report1.pdf report2.pdf presentation.pdf \
  --persona "Project Manager" \
  --job "Create project status dashboard"
```

### Different Output Formats
```bash
# JSON only
python cli_offline.py --format json --persona "Student" --job "Study for exam"

# Summary only  
python cli_offline.py --format summary --persona "Analyst" --job "Investment research"

# Both (default)
python cli_offline.py --format both --persona "HR" --job "Policy updates"
```

## Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--input` | `-i` | Input directory or single PDF file | `--input ./documents` |
| `--files` | `-f` | Specific PDF files to process | `--files doc1.pdf doc2.pdf` |
| `--output` | `-o` | Output directory (default: ./output) | `--output ./results` |
| `--persona` | `-p` | Your role/persona | `--persona "HR Professional"` |
| `--job` | `-j` | Your job-to-be-done | `--job "Create onboarding forms"` |
| `--format` | | Output format: json, summary, both | `--format summary` |
| `--quiet` | `-q` | Minimal output | `--quiet` |

## Persona Examples

### HR Professional
```bash
python cli_offline.py \
  --persona "HR Professional" \
  --job "Create and manage fillable forms for employee onboarding"
```

**Expected Output**: Sections focused on workflow automation, digital form management, compliance documentation, and e-signature integration.

### Student  
```bash
python cli_offline.py \
  --persona "Graduate Student" \
  --job "Prepare comprehensive study materials for upcoming examination"
```

**Expected Output**: Key concepts, practice problems, study guides, and exam-focused content with simplified explanations.

### Data Analyst
```bash
python cli_offline.py \
  --persona "Business Data Analyst" \
  --job "Extract actionable insights for quarterly business review"
```

**Expected Output**: Market trends, performance metrics, data visualizations, and strategic recommendations.

## Output Structure

The system generates structured JSON output with:

- **Metadata**: Document info, processing summary, timestamps
- **Extracted Sections**: Ranked sections with persona-adaptive titles
- **Subsection Analysis**: Detailed analysis with actionable insights
- **Relevance Scores**: Multi-factor scoring (semantic similarity, keyword matching, etc.)

### Sample Output
```json
{
  "metadata": {
    "persona": "HR Professional",
    "job_to_be_done": "Streamline onboarding process",
    "total_documents": 3,
    "processing_time": 4.2
  },
  "extracted_sections": [
    {
      "document": "handbook.pdf",
      "page_number": 15,
      "original_section_title": "New Employee Setup",
      "persona_adapted_title": "Digital Onboarding Workflow Optimization",
      "importance_rank": 1,
      "relevance_scores": {
        "total_score": 0.89
      },
      "content_preview": "Automated workflows can reduce onboarding time...",
      "actionable_insights": [
        "Implement e-signature integration",
        "Create automated form routing system"
      ]
    }
  ]
}
```

## File Organization

```
project/
├── cli_offline.py          # Standalone CLI script
├── run_cli.sh             # Linux/Mac runner
├── run_cli.bat            # Windows runner  
├── input/                 # Place your PDFs here
├── output/                # Analysis results
├── Dockerfile             # Container configuration
└── docker-compose.yml     # Multi-container setup
```

## Troubleshooting

### No PDFs Found
- Ensure PDFs are in `./input` directory, or use `--input` to specify location
- Check file permissions and that files have `.pdf` extension

### Missing Dependencies  
- The offline CLI works without dependencies (demo mode)
- For full functionality: `pip install -r requirements.txt`
- Or use Docker for isolated environment

### Output Issues
- Check write permissions in output directory
- Use `--output` to specify different location
- Try `--quiet` mode to reduce output verbosity

## Performance Notes

- **CPU Optimized**: Uses lightweight models suitable for CPU-only execution
- **Memory Efficient**: Processes documents incrementally to minimize RAM usage  
- **Time Constraints**: Designed for <60 second processing of 3-5 documents
- **Offline Capable**: Works without internet connection after initial setup

## Advanced Usage

### Batch Processing
```bash
# Process multiple directories
for dir in reports_q1 reports_q2 reports_q3; do
  python cli_offline.py --input $dir --output results_$dir --persona "Analyst" --job "Quarterly review"
done
```

### Integration with Other Tools
```bash
# Convert output to CSV for spreadsheet analysis
python -c "
import json, csv
with open('output/analysis_results.json') as f:
    data = json.load(f)
    
with open('sections.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'document', 'score'])
    writer.writeheader()
    for section in data['extracted_sections']:
        writer.writerow({
            'title': section['persona_adapted_title'],
            'document': section['document'], 
            'score': section['relevance_scores']['total_score']
        })
"
```
