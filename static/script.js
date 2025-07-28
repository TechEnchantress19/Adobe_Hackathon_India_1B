/**
 * Frontend JavaScript for Persona-Driven PDF Analysis System
 * Handles form submission, file upload, progress tracking, and results display
 */

// Global variables
let currentResults = null;
let isProcessing = false;

// DOM Ready
// Language switching function
function setLanguage(locale) {
    fetch(`/set_language/${locale}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            }
        })
        .catch(error => console.error('Error setting language:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializePersonaExamples();
    initializeFileUpload();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    const form = document.getElementById('analysisForm');
    const submitBtn = document.getElementById('submitBtn');

    if (form) {
        form.addEventListener('submit', handleFormSubmission);
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            if (isProcessing) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Add input validation listeners
    const personaInput = document.getElementById('persona');
    const jobInput = document.getElementById('job_to_be_done');
    const fileInput = document.getElementById('pdf_files');

    if (personaInput) {
        personaInput.addEventListener('input', validateForm);
    }
    if (jobInput) {
        jobInput.addEventListener('input', validateForm);
    }
    if (fileInput) {
        fileInput.addEventListener('change', validateForm);
    }
}

/**
 * Initialize persona example buttons
 */
function initializePersonaExamples() {
    const exampleButtons = document.querySelectorAll('.persona-example');
    
    exampleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const persona = this.getAttribute('data-persona');
            const job = this.getAttribute('data-job');
            
            document.getElementById('persona').value = persona;
            document.getElementById('job_to_be_done').value = job;
            
            // Add visual feedback
            this.classList.add('btn-primary');
            this.classList.remove('btn-outline-secondary');
            
            // Reset other buttons
            exampleButtons.forEach(btn => {
                if (btn !== this) {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-secondary');
                }
            });
            
            validateForm();
        });
    });
}

/**
 * Initialize file upload functionality
 */
function initializeFileUpload() {
    const fileInput = document.getElementById('pdf_files');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const files = this.files;
            let totalSize = 0;
            let validFiles = 0;
            
            // Validate files
            Array.from(files).forEach(file => {
                if (file.type === 'application/pdf') {
                    validFiles++;
                    totalSize += file.size;
                }
            });
            
            // Update file input feedback
            const feedbackDiv = this.parentNode.querySelector('.form-text');
            if (feedbackDiv) {
                if (validFiles === 0) {
                    feedbackDiv.innerHTML = '<span class="text-danger">Please select PDF files only</span>';
                } else if (totalSize > 50 * 1024 * 1024) {
                    feedbackDiv.innerHTML = '<span class="text-danger">Total file size exceeds 50MB limit</span>';
                } else {
                    const sizeMB = (totalSize / (1024 * 1024)).toFixed(1);
                    feedbackDiv.innerHTML = `<span class="text-success">${validFiles} PDF file(s) selected (${sizeMB}MB)</span>`;
                }
            }
            
            validateForm();
        });
    }
}

/**
 * Validate form inputs
 */
function validateForm() {
    const persona = document.getElementById('persona').value.trim();
    const job = document.getElementById('job_to_be_done').value.trim();
    const files = document.getElementById('pdf_files').files;
    const submitBtn = document.getElementById('submitBtn');
    
    let isValid = true;
    let validFiles = 0;
    let totalSize = 0;
    
    // Validate files
    Array.from(files).forEach(file => {
        if (file.type === 'application/pdf') {
            validFiles++;
            totalSize += file.size;
        }
    });
    
    // Check validation criteria
    if (!persona || !job || validFiles === 0 || totalSize > 50 * 1024 * 1024) {
        isValid = false;
    }
    
    // Update submit button
    if (submitBtn) {
        submitBtn.disabled = !isValid || isProcessing;
        
        if (isProcessing) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        } else if (isValid) {
            submitBtn.innerHTML = '<i class="fas fa-cogs me-2"></i>Analyze PDFs';
        } else {
            submitBtn.innerHTML = '<i class="fas fa-cogs me-2"></i>Analyze PDFs';
        }
    }
    
    return isValid;
}

/**
 * Handle form submission
 */
async function handleFormSubmission(event) {
    event.preventDefault();
    
    if (isProcessing || !validateForm()) {
        return false;
    }
    
    // Set processing state
    isProcessing = true;
    
    // Show progress indicator
    showProgress();
    hideError();
    hideResults();
    
    try {
        const formData = new FormData();
        const persona = document.getElementById('persona').value.trim();
        const job = document.getElementById('job_to_be_done').value.trim();
        const files = document.getElementById('pdf_files').files;
        
        // Add form data
        formData.append('persona', persona);
        formData.append('job_to_be_done', job);
        
        // Add files
        Array.from(files).forEach(file => {
            if (file.type === 'application/pdf') {
                formData.append('pdf_files', file);
            }
        });
        
        // Submit form
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Success - display results
            currentResults = result;
            displayResults(result);
            showResults();
        } else {
            // Error - show error message
            showError(result.error || 'An error occurred during processing');
        }
        
    } catch (error) {
        console.error('Error submitting form:', error);
        showError('Network error: Unable to connect to the server');
    } finally {
        // Reset processing state
        isProcessing = false;
        hideProgress();
        validateForm(); // Update button state
    }
    
    return false;
}

/**
 * Show progress indicator
 */
function showProgress() {
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'block';
        progressContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Hide progress indicator
 */
function hideProgress() {
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorAlert && errorMessage) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Hide error message
 */
function hideError() {
    const errorAlert = document.getElementById('errorAlert');
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
}

/**
 * Show results container
 */
function showResults() {
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Hide results container
 */
function hideResults() {
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    const container = document.getElementById('resultsContainer');
    if (!container || !data) return;
    
    const metadata = data.metadata;
    let html = `
        <div class="card shadow-sm mb-4 fade-in">
            <div class="card-header bg-success text-white">
                <h5 class="card-title mb-0">
                    <i class="fas fa-check-circle me-2"></i>
                    Analysis Complete
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-user me-2"></i>Persona Context</h6>
                        <p><strong>Persona:</strong> ${metadata.persona}</p>
                        <p><strong>Job-to-be-done:</strong> ${metadata.job_to_be_done}</p>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-chart-bar me-2"></i>Processing Summary</h6>
                        <div class="row text-center">
                            <div class="col-4">
                                <div class="bg-light p-2 rounded">
                                    <h4 class="text-primary mb-0">${metadata.processing_summary.total_documents}</h4>
                                    <small>Documents</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="bg-light p-2 rounded">
                                    <h4 class="text-success mb-0">${metadata.processing_summary.total_sections_analyzed}</h4>
                                    <small>Sections</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="bg-light p-2 rounded">
                                    <h4 class="text-info mb-0">${metadata.processing_summary.total_tables_found}</h4>
                                    <small>Tables</small>
                                </div>
                            </div>
                        </div>
                        ${data.processing_time ? `<p class="mt-2 mb-0"><small><strong>Processing Time:</strong> ${data.processing_time}s</small></p>` : ''}
                    </div>
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary me-2" onclick="downloadResults()">
                        <i class="fas fa-download me-1"></i>
                        Download JSON
                    </button>
                    <button class="btn btn-outline-secondary" onclick="copyToClipboard()">
                        <i class="fas fa-copy me-1"></i>
                        Copy Results
                    </button>
                </div>
            </div>
        </div>
    `;

    // Top Ranked Sections
    html += `
        <div class="card shadow-sm mb-4 fade-in">
            <div class="card-header bg-light">
                <h5 class="card-title mb-0">
                    <i class="fas fa-trophy me-2"></i>
                    Top Ranked Sections
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
    `;

    // Display top 6 sections in cards
    data.extracted_sections.slice(0, 6).forEach((section, index) => {
        const scorePercentage = (section.relevance_scores.total_score * 100).toFixed(1);
        const scoreColor = section.relevance_scores.total_score > 0.7 ? 'success' : 
                          section.relevance_scores.total_score > 0.4 ? 'warning' : 'secondary';
        
        html += `
            <div class="col-md-6 mb-3">
                <div class="card border-${scoreColor}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-primary">#${section.importance_rank}</span>
                            <span class="badge bg-${scoreColor}">${scorePercentage}%</span>
                        </div>
                        <h6 class="card-title">${section.persona_adapted_title}</h6>
                        <p class="card-text">
                            <small class="text-muted">
                                <i class="fas fa-file me-1"></i>${section.document} • 
                                <i class="fas fa-file-alt me-1"></i>Page ${section.page_number}
                            </small>
                        </p>
                        ${section.original_section_title !== section.persona_adapted_title ? 
                          `<p class="card-text"><small class="text-muted">Original: ${section.original_section_title}</small></p>` : ''}
                        <div class="score-bar mb-2">
                            <div class="score-fill score-${scoreColor === 'warning' ? 'medium' : scoreColor === 'success' ? 'high' : 'low'}" 
                                 style="width: ${scorePercentage}%"></div>
                        </div>
                        <button class="btn btn-sm btn-outline-info" onclick="showSectionDetails(${index})">
                            <i class="fas fa-eye me-1"></i>View Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    html += `
                </div>
                <div class="text-center mt-3">
                    <button class="btn btn-outline-primary" onclick="toggleAllSections()">
                        <i class="fas fa-list me-1"></i>
                        View All Sections
                    </button>
                </div>
            </div>
        </div>
    `;

    // Detailed Analysis
    html += `
        <div class="card shadow-sm mb-4 fade-in">
            <div class="card-header bg-light">
                <h5 class="card-title mb-0">
                    <i class="fas fa-microscope me-2"></i>
                    Detailed Analysis (Top ${Math.min(5, data.subsection_analysis.length)})
                </h5>
            </div>
            <div class="card-body">
                <div class="accordion" id="analysisAccordion">
    `;

    // Top subsections
    data.subsection_analysis.slice(0, 5).forEach((subsection, index) => {
        html += `
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading${index}">
                    <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" 
                            type="button" data-bs-toggle="collapse" 
                            data-bs-target="#collapse${index}">
                        <div class="d-flex w-100 justify-content-between align-items-center me-3">
                            <span>
                                <strong>${subsection.persona_adapted_title}</strong>
                                <small class="text-muted ms-2">(${subsection.document})</small>
                            </span>
                            <span class="badge bg-primary">Rank #${subsection.importance_rank}</span>
                        </div>
                    </button>
                </h2>
                <div id="collapse${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                     data-bs-parent="#analysisAccordion">
                    <div class="accordion-body">
                        <div class="row">
                            <div class="col-md-8">
                                <h6><i class="fas fa-file-text me-2"></i>Refined Summary</h6>
                                <div class="section-detail">
                                    ${subsection.refined_text}
                                </div>
                                
                                <h6><i class="fas fa-lightbulb me-2"></i>Actionable Insights</h6>
                                <ul class="list-unstyled">
        `;

        subsection.actionable_insights.forEach(insight => {
            html += `<li><i class="fas fa-arrow-right text-primary me-2"></i>${insight}</li>`;
        });

        html += `
                                </ul>
                            </div>
                            <div class="col-md-4">
                                <div class="bg-light p-3 rounded">
                                    <h6><i class="fas fa-info-circle me-2"></i>Section Details</h6>
                                    <p><small><strong>Document:</strong> ${subsection.document}</small></p>
                                    <p><small><strong>Page:</strong> ${subsection.page_number}</small></p>
                                    <p><small><strong>Original Title:</strong> ${subsection.section_title}</small></p>
        `;

        if (subsection.table_integration) {
            html += `
                                    <div class="mt-3">
                                        <h6><i class="fas fa-table me-2"></i>Table Data</h6>
                                        <p><small>${subsection.table_integration.table_count} table(s) with ${subsection.table_integration.total_rows} total rows</small></p>
                                        <button class="btn btn-sm btn-outline-info" onclick="showTableDetails(${index})">
                                            <i class="fas fa-table me-1"></i>View Tables
                                        </button>
                                    </div>
            `;
        }

        html += `
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    html += `
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

/**
 * Show detailed section information
 */
function showSectionDetails(index) {
    if (!currentResults || !currentResults.extracted_sections[index]) {
        return;
    }
    
    const section = currentResults.extracted_sections[index];
    const scores = section.relevance_scores;
    
    let modalHtml = `
        <div class="modal fade" id="sectionModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <span class="badge bg-primary me-2">#${section.importance_rank}</span>
                            ${section.persona_adapted_title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <h6>Document Information</h6>
                                <p><strong>File:</strong> ${section.document}</p>
                                <p><strong>Page:</strong> ${section.page_number}</p>
                                <p><strong>Word Count:</strong> ${section.word_count}</p>
                                <p><strong>Has Tables:</strong> ${section.has_tables ? 'Yes' : 'No'}</p>
                            </div>
                            <div class="col-md-6">
                                <h6>Relevance Scores</h6>
                                <div class="mb-2">
                                    <small>Semantic Similarity: <strong>${(scores.semantic_similarity * 100).toFixed(1)}%</strong></small>
                                    <div class="progress" style="height: 6px;">
                                        <div class="progress-bar" style="width: ${scores.semantic_similarity * 100}%"></div>
                                    </div>
                                </div>
                                <div class="mb-2">
                                    <small>Keyword Match: <strong>${(scores.keyword_match * 100).toFixed(1)}%</strong></small>
                                    <div class="progress" style="height: 6px;">
                                        <div class="progress-bar bg-success" style="width: ${scores.keyword_match * 100}%"></div>
                                    </div>
                                </div>
                                <div class="mb-2">
                                    <small>Heading Weight: <strong>${(scores.heading_weight * 100).toFixed(1)}%</strong></small>
                                    <div class="progress" style="height: 6px;">
                                        <div class="progress-bar bg-info" style="width: ${scores.heading_weight * 100}%"></div>
                                    </div>
                                </div>
                                <div class="mb-2">
                                    <small>Content Quality: <strong>${(scores.content_quality * 100).toFixed(1)}%</strong></small>
                                    <div class="progress" style="height: 6px;">
                                        <div class="progress-bar bg-warning" style="width: ${scores.content_quality * 100}%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <h6>Content Preview</h6>
                            <div class="bg-light p-3 rounded">
                                ${section.content_preview}
                            </div>
                        </div>
                        ${section.original_section_title !== section.persona_adapted_title ? 
                          `<div class="mb-3">
                               <h6>Original Title</h6>
                               <p class="text-muted">${section.original_section_title}</p>
                           </div>` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('sectionModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('sectionModal'));
    modal.show();
}

/**
 * Show table details
 */
function showTableDetails(index) {
    if (!currentResults || !currentResults.subsection_analysis[index] || 
        !currentResults.subsection_analysis[index].table_integration) {
        return;
    }
    
    const tableData = currentResults.subsection_analysis[index].table_integration;
    
    let modalHtml = `
        <div class="modal fade" id="tableModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-table me-2"></i>
                            Table Data Analysis
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <h6>Table Summary</h6>
                                <p><strong>Number of Tables:</strong> ${tableData.table_count}</p>
                                <p><strong>Total Rows:</strong> ${tableData.total_rows}</p>
                                <p><strong>Total Columns:</strong> ${tableData.total_columns}</p>
                            </div>
                        </div>
    `;
    
    // Display each table
    tableData.table_details.forEach((table, tableIndex) => {
        modalHtml += `
            <div class="mb-4">
                <h6>Table ${table.table_index}</h6>
                <p><small>Rows: ${table.rows} | Columns: ${table.columns} | Source: ${table.source}</small></p>
                
                ${table.headers.length > 0 ? `
                    <div class="table-responsive">
                        <table class="table table-sm table-bordered">
                            <thead>
                                <tr>
                                    ${table.headers.map(header => `<th>${header}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${table.sample_data.map(row => 
                                    `<tr>${Object.values(row).map(cell => `<td>${cell || ''}</td>`).join('')}</tr>`
                                ).join('')}
                            </tbody>
                        </table>
                    </div>
                    ${table.rows > table.sample_data.length ? 
                      `<p><small class="text-muted">Showing first ${table.sample_data.length} rows of ${table.rows}</small></p>` : ''}
                ` : '<p class="text-muted">No structured data available</p>'}
            </div>
        `;
    });
    
    modalHtml += `
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('tableModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('tableModal'));
    modal.show();
}

/**
 * Toggle display of all sections
 */
function toggleAllSections() {
    // This would expand to show all sections in a detailed view
    // For now, just scroll to the detailed analysis
    const detailedSection = document.querySelector('.accordion');
    if (detailedSection) {
        detailedSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Download results as JSON file
 */
function downloadResults() {
    if (!currentResults) {
        showError('No results available to download');
        return;
    }
    
    try {
        const dataStr = JSON.stringify(currentResults, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `persona_analysis_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success message
        showTemporaryMessage('Results downloaded successfully!', 'success');
        
    } catch (error) {
        console.error('Download error:', error);
        showError('Failed to download results');
    }
}

/**
 * Copy results to clipboard
 */
async function copyToClipboard() {
    if (!currentResults) {
        showError('No results available to copy');
        return;
    }
    
    try {
        const dataStr = JSON.stringify(currentResults, null, 2);
        await navigator.clipboard.writeText(dataStr);
        showTemporaryMessage('Results copied to clipboard!', 'success');
    } catch (error) {
        console.error('Copy error:', error);
        showError('Failed to copy results to clipboard');
    }
}

/**
 * Show temporary success/info message
 */
function showTemporaryMessage(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="tempAlert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert after the header
    const header = document.querySelector('.bg-primary').parentNode;
    header.insertAdjacentHTML('afterend', alertHtml);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        const alert = document.getElementById('tempAlert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 3000);
}

/**
 * Utility function to format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Utility function to sanitize HTML
 */
function sanitizeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions for potential external use
window.PersonaAnalysisApp = {
    downloadResults,
    copyToClipboard,
    showSectionDetails,
    showTableDetails,
    currentResults: () => currentResults
};
