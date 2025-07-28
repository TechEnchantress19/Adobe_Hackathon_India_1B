FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir PyMuPDF pdfplumber camelot-py[base] sentence-transformers flask pandas numpy scikit-learn

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=main.py

# Default command (can be overridden)
CMD ["python", "main.py", "--web", "--port", "5000"]