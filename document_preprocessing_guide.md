# Document Preprocessing Guide for Credit Agreement RAG Systems

## Table of Contents
1. [Overview](#overview)
2. [Credit Agreement Document Structure](#credit-agreement-document-structure)
3. [Preprocessing Strategy](#preprocessing-strategy)
4. [Chunking Guidelines](#chunking-guidelines)
5. [Metadata Enhancement](#metadata-enhancement)
6. [Special Handling Requirements](#special-handling-requirements)
7. [Implementation Examples](#implementation-examples)
8. [Quality Assurance](#quality-assurance)

---

## Overview

Credit agreements, compliance certificates, and related financial documents require specialized preprocessing to ensure optimal retrieval performance. Unlike general documents, credit agreements have specific structural patterns, hierarchical organization, and cross-referencing that must be preserved during chunking.

### Key Challenges

1. **Long, complex definitions** that span multiple pages
2. **Hierarchical section numbering** (e.g., Section 6.12(a)(i)(A))
3. **Cross-references** between sections
4. **Tables and schedules** (pricing grids, covenant matrices)
5. **Legal language** with nested clauses
6. **Financial formulas** that must remain intact

---

## Credit Agreement Document Structure

### Typical LSTA Credit Agreement Structure

```
├── ARTICLE I: DEFINITIONS AND ACCOUNTING TERMS
│   └── Section 1.01: Defined Terms
│   └── Section 1.02: Classification of Loans and Borrowings
│   └── Section 1.03: Terms Generally
│   └── Section 1.04: Accounting Terms; GAAP
│
├── ARTICLE II: THE CREDITS
│   └── Section 2.01: Commitments
│   └── Section 2.02: Loans and Borrowings
│   └── Section 2.03: Requests for Borrowings
│   └── [...]
│
├── ARTICLE III: TAXES, YIELD PROTECTION AND ILLEGALITY
│   └── Section 3.01: Taxes
│   └── [...]
│
├── ARTICLE IV: CONDITIONS PRECEDENT TO CREDIT EXTENSIONS
│
├── ARTICLE V: REPRESENTATIONS AND WARRANTIES
│
├── ARTICLE VI: AFFIRMATIVE COVENANTS
│   └── Section 6.01: Financial Statements
│   └── Section 6.02: Certificates; Other Information
│   └── [...]
│
├── ARTICLE VII: NEGATIVE COVENANTS
│   └── Section 7.01: Liens
│   └── Section 7.02: Indebtedness
│   └── Section 7.03: Investments
│   └── [...]
│
├── ARTICLE VIII: EVENTS OF DEFAULT AND REMEDIES
│   └── Section 8.01: Events of Default
│   └── Section 8.02: Remedies Upon Event of Default
│
├── ARTICLE IX: ADMINISTRATIVE AGENT
│
├── ARTICLE X: MISCELLANEOUS
│
└── SCHEDULES AND EXHIBITS
    ├── Schedule 1.01: Existing Letters of Credit
    ├── Schedule 2.01: Commitments
    ├── Exhibit A: Form of Compliance Certificate
    └── [...]
```

### Compliance Certificate Structure

```
├── Header Information
│   └── Borrower name
│   └── Certificate date
│   └── Testing period
│
├── Certificate of Compliance
│   └── Officer attestation
│
├── Financial Covenant Calculations
│   ├── Covenant 1: [Name]
│   │   └── Formula
│   │   └── Calculation
│   │   └── Requirement vs Actual
│   │   └── Compliance status
│   ├── Covenant 2: [Name]
│   └── [...]
│
├── Supporting Schedules
│   ├── Schedule A: Financial Statement Details
│   ├── Schedule B: Debt Schedule
│   └── [...]
│
└── Officer Signature
```

---

## Preprocessing Strategy

### Phase 1: Document Loading and Cleaning

#### 1.1 Extract Text with Structure Preservation

**For PDFs:**
```python
from langchain_community.document_loaders import PyPDFLoader
import pdfplumber

def load_pdf_with_structure(file_path):
    """
    Load PDF while preserving structure like tables and formatting.
    """
    # Use pdfplumber for better table extraction
    with pdfplumber.open(file_path) as pdf:
        pages_content = []
        
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text
            text = page.extract_text()
            
            # Extract tables separately
            tables = page.extract_tables()
            
            # Combine text and tables
            page_content = {
                'page_number': page_num,
                'text': text,
                'tables': tables,
                'has_tables': len(tables) > 0
            }
            
            pages_content.append(page_content)
    
    return pages_content
```

**For Word Documents:**
```python
from docx import Document
import docx2txt

def load_docx_with_structure(file_path):
    """
    Load DOCX while preserving structure including tables.
    """
    doc = Document(file_path)
    
    content = []
    
    for element in doc.element.body:
        if element.tag.endswith('p'):  # Paragraph
            para = element
            text = para.text
            # Check for heading styles
            style = para.style.name if hasattr(para, 'style') else None
            
            content.append({
                'type': 'paragraph',
                'text': text,
                'style': style
            })
            
        elif element.tag.endswith('tbl'):  # Table
            # Extract table data
            table_data = extract_table_from_element(element)
            
            content.append({
                'type': 'table',
                'data': table_data
            })
    
    return content
```

#### 1.2 Text Cleaning

```python
import re

def clean_credit_agreement_text(text):
    """
    Clean text while preserving important formatting.
    """
    # Remove excessive whitespace but preserve section breaks
    text = re.sub(r'\n\n\n+', '\n\n', text)
    
    # Fix common OCR errors in financial documents
    text = text.replace('l,', '1,')  # Common OCR mistake
    text = text.replace('O%', '0%')  # Zero vs O
    
    # Preserve section numbers - DON'T remove them
    # e.g., "Section 6.12(a)(i)" should stay intact
    
    # Remove page headers/footers but keep section headers
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Preserve financial formatting
    # Keep dollar signs, percentages, ratios (e.g., "4.50:1.00")
    
    return text.strip()
```

---

## Chunking Guidelines

### Recommended Chunk Sizes

| Document Type | Chunk Size | Overlap | Rationale |
|---------------|------------|---------|-----------|
| Definitions (Article I) | 800-1200 tokens | 150-200 tokens | Definitions can be long; overlap ensures cross-references preserved |
| Covenant Sections | 1000-1500 tokens | 200-250 tokens | Covenants have exceptions and sub-clauses that need context |
| Pricing Grids | 400-600 tokens | 100 tokens | Tables should stay together; smaller chunks for precision |
| Events of Default | 1000-1500 tokens | 200 tokens | Each event type should be complete |
| Compliance Certificates | 600-1000 tokens | 150 tokens | Each covenant calculation should be complete |

### Intelligent Chunking Strategy

#### 1. Hierarchical Chunking

Credit agreements should be chunked respecting their hierarchical structure:

```python
class CreditAgreementChunker:
    """
    Intelligent chunker that respects credit agreement structure.
    """
    
    def __init__(self):
        self.section_pattern = re.compile(
            r'(?:SECTION|Section)\s+(\d+(?:\.\d+)*(?:\([a-z]\))?(?:\([ivxlcdm]+\))?)',
            re.IGNORECASE
        )
        self.article_pattern = re.compile(
            r'(?:ARTICLE|Article)\s+([IVXLCDM]+|\d+)',
            re.IGNORECASE
        )
    
    def chunk_by_sections(self, text, max_chunk_size=1200, overlap=200):
        """
        Chunk text by sections while respecting size limits.
        """
        chunks = []
        
        # Find all section boundaries
        sections = list(self.section_pattern.finditer(text))
        
        for i, section_match in enumerate(sections):
            start_pos = section_match.start()
            
            # Find end position (start of next section or end of text)
            if i + 1 < len(sections):
                end_pos = sections[i + 1].start()
            else:
                end_pos = len(text)
            
            section_text = text[start_pos:end_pos]
            section_number = section_match.group(1)
            
            # If section is small enough, keep it as one chunk
            if len(section_text) <= max_chunk_size:
                chunks.append({
                    'text': section_text,
                    'section': section_number,
                    'type': 'complete_section'
                })
            else:
                # Section is too large, split it intelligently
                sub_chunks = self._split_large_section(
                    section_text,
                    section_number,
                    max_chunk_size,
                    overlap
                )
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _split_large_section(self, text, section_number, max_size, overlap):
        """
        Split a large section into smaller chunks at natural boundaries.
        """
        # Try to split at sub-section boundaries first
        subsection_pattern = re.compile(r'\([a-z]\)|\([ivxlcdm]+\)')
        splits = list(subsection_pattern.finditer(text))
        
        if splits:
            # Split at subsections
            chunks = []
            for i, split in enumerate(splits):
                start = split.start()
                end = splits[i+1].start() if i+1 < len(splits) else len(text)
                
                chunk_text = text[start:end]
                if len(chunk_text) <= max_size:
                    chunks.append({
                        'text': chunk_text,
                        'section': f"{section_number}{split.group()}",
                        'type': 'subsection'
                    })
                else:
                    # Still too large, use recursive splitting
                    sub_chunks = self._split_at_sentences(
                        chunk_text,
                        max_size,
                        overlap
                    )
                    chunks.extend(sub_chunks)
            
            return chunks
        else:
            # No subsections, split at sentence boundaries
            return self._split_at_sentences(text, max_size, overlap)
    
    def _split_at_sentences(self, text, max_size, overlap):
        """
        Split text at sentence boundaries when no structural splits available.
        """
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_size,
            chunk_overlap=overlap,
            separators=[
                ".\n",          # End of sentence with newline
                "; ",           # Semicolon (common in legal documents)
                ". ",           # End of sentence
                ",\n",          # Comma with newline
                "\n\n",         # Paragraph break
                "\n",           # Line break
                " ",            # Word break
            ]
        )
        
        return splitter.split_text(text)
```

#### 2. Special Handling for Key Sections

**Definitions Section:**
```python
def chunk_definitions(definition_section_text):
    """
    Chunk the definitions section, keeping each definition complete.
    """
    # Pattern to identify defined terms (typically in quotes or bold)
    # e.g., "EBITDA" means...
    term_pattern = re.compile(r'"([^"]+)"\s+means')
    
    chunks = []
    terms = list(term_pattern.finditer(definition_section_text))
    
    for i, term_match in enumerate(terms):
        term_name = term_match.group(1)
        start_pos = term_match.start()
        
        # Find end (start of next term or end of section)
        if i + 1 < len(terms):
            end_pos = terms[i + 1].start()
        else:
            end_pos = len(definition_section_text)
        
        definition_text = definition_section_text[start_pos:end_pos]
        
        # If definition is very long (>1500 tokens), may need to split
        # but include overlap to preserve cross-references
        if len(definition_text) > 1500:
            # Split but ensure term name is in each chunk
            sub_chunks = split_long_definition(definition_text, term_name)
            chunks.extend(sub_chunks)
        else:
            chunks.append({
                'text': definition_text,
                'term': term_name,
                'type': 'definition'
            })
    
    return chunks
```

**Pricing Grids and Tables:**
```python
def extract_and_chunk_tables(page_content):
    """
    Extract tables and create special chunks for them.
    """
    chunks = []
    
    # Tables should generally stay together
    for table in page_content.get('tables', []):
        # Convert table to markdown format for better LLM understanding
        table_markdown = convert_table_to_markdown(table)
        
        # Add context from surrounding text
        context = extract_table_context(page_content['text'], table)
        
        chunk = {
            'text': f"{context}\n\n{table_markdown}",
            'type': 'table',
            'table_type': identify_table_type(table)  # 'pricing_grid', 'covenant_matrix', etc.
        }
        
        chunks.append(chunk)
    
    return chunks

def convert_table_to_markdown(table_data):
    """
    Convert table data to markdown format.
    """
    if not table_data or len(table_data) == 0:
        return ""
    
    # Get headers (first row)
    headers = table_data[0]
    
    # Create markdown table
    markdown = "| " + " | ".join(str(h) for h in headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # Add data rows
    for row in table_data[1:]:
        markdown += "| " + " | ".join(str(cell) for cell in row) + " |\n"
    
    return markdown
```

**Financial Covenants:**
```python
def chunk_covenant_section(covenant_text, covenant_name):
    """
    Chunk covenant sections keeping requirements and exceptions together.
    """
    chunks = []
    
    # Pattern for "provided that" and "except" clauses
    exception_pattern = re.compile(
        r'(?:provided(?:\s+that)?|except(?:\s+that)?|excluding)',
        re.IGNORECASE
    )
    
    # Main covenant requirement should be in first chunk
    # Include first exception if it fits
    
    # Split into main requirement and exceptions
    parts = exception_pattern.split(covenant_text)
    
    current_chunk = f"Covenant: {covenant_name}\n\n"
    current_chunk += parts[0]  # Main requirement
    
    # Add exceptions one by one, creating new chunks if needed
    for i, part in enumerate(parts[1:], 1):
        exception_text = f"\n\nException {i}: {part}"
        
        if len(current_chunk) + len(exception_text) <= 1200:
            current_chunk += exception_text
        else:
            # Save current chunk and start new one
            chunks.append({
                'text': current_chunk,
                'covenant': covenant_name,
                'type': 'covenant',
                'part': 'main' if i == 1 else f'exceptions_{i}'
            })
            
            current_chunk = f"Covenant: {covenant_name} (continued)\n\n{exception_text}"
    
    # Add final chunk
    chunks.append({
        'text': current_chunk,
        'covenant': covenant_name,
        'type': 'covenant',
        'part': 'final'
    })
    
    return chunks
```

---

## Metadata Enhancement

### Essential Metadata Fields

For each chunk, include the following metadata:

```python
chunk_metadata = {
    # Document identification
    'filename': 'Senior_Credit_Agreement_2024.pdf',
    'document_type': 'Credit Agreement',  # or 'Compliance Certificate', 'Credit Application'
    'document_date': '2024-03-15',
    
    # Location within document
    'page': 42,
    'article': 'VII',
    'section': '7.02',
    'subsection': '(a)(i)',
    
    # Content classification
    'content_type': 'covenant',  # 'definition', 'pricing', 'event_of_default', etc.
    'covenant_type': 'negative',  # if applicable: 'financial', 'negative', 'affirmative'
    'covenant_name': 'Limitation on Indebtedness',  # if applicable
    
    # Chunk information
    'chunk_id': 142,
    'total_chunks': 523,
    'is_complete_section': False,
    'has_table': False,
    'has_formula': True,
    
    # Cross-references
    'references': ['Section 1.01', 'Section 7.01'],  # Sections referenced in this chunk
    'defined_terms': ['Consolidated Total Debt', 'EBITDA'],  # Defined terms used
    
    # Financial markers
    'contains_amounts': True,
    'contains_percentages': True,
    'contains_ratios': True,
    'contains_dates': True,
}
```

### Metadata Extraction Functions

```python
import re
from datetime import datetime

def extract_metadata(chunk_text, document_info):
    """
    Extract rich metadata from chunk text.
    """
    metadata = {
        'filename': document_info['filename'],
        'document_type': document_info['type'],
        'page': document_info.get('page'),
    }
    
    # Extract section information
    section_match = re.search(
        r'(?:SECTION|Section)\s+(\d+(?:\.\d+)*(?:\([a-z]\))?(?:\([ivxlcdm]+\))?)',
        chunk_text,
        re.IGNORECASE
    )
    if section_match:
        metadata['section'] = section_match.group(1)
    
    # Extract article information
    article_match = re.search(
        r'(?:ARTICLE|Article)\s+([IVXLCDM]+|\d+)',
        chunk_text,
        re.IGNORECASE
    )
    if article_match:
        metadata['article'] = article_match.group(1)
    
    # Identify content type
    metadata['content_type'] = identify_content_type(chunk_text)
    
    # Extract financial markers
    metadata['contains_amounts'] = bool(re.search(r'\$[\d,]+', chunk_text))
    metadata['contains_percentages'] = bool(re.search(r'\d+\.?\d*%', chunk_text))
    metadata['contains_ratios'] = bool(re.search(r'\d+\.?\d*:\d+\.?\d*', chunk_text))
    metadata['contains_dates'] = bool(re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', chunk_text))
    
    # Extract cross-references
    metadata['references'] = extract_cross_references(chunk_text)
    
    # Extract defined terms (capitalized terms)
    metadata['defined_terms'] = extract_defined_terms(chunk_text)
    
    # Check for tables
    metadata['has_table'] = '|' in chunk_text or 'table' in chunk_text.lower()
    
    return metadata

def identify_content_type(text):
    """
    Identify what type of content this chunk contains.
    """
    text_lower = text.lower()
    
    if 'means' in text_lower and ('"' in text or 'definition' in text_lower):
        return 'definition'
    elif any(term in text_lower for term in ['covenant', 'shall not', 'shall maintain']):
        return 'covenant'
    elif any(term in text_lower for term in ['pricing', 'interest rate', 'margin', 'applicable rate']):
        return 'pricing'
    elif 'event of default' in text_lower:
        return 'event_of_default'
    elif 'representation' in text_lower or 'warranty' in text_lower:
        return 'representation'
    elif any(term in text_lower for term in ['compliance certificate', 'covenant calculation']):
        return 'compliance_data'
    else:
        return 'general'

def extract_cross_references(text):
    """
    Extract references to other sections in the document.
    """
    # Pattern: "Section X.XX" or "clause (a)" etc.
    pattern = re.compile(
        r'(?:Section|section|clause|subsection)\s+(\d+\.?\d*(?:\([a-z]\))?(?:\([ivxlcdm]+\))?)',
        re.IGNORECASE
    )
    
    references = [match.group(1) for match in pattern.finditer(text)]
    return list(set(references))  # Remove duplicates

def extract_defined_terms(text):
    """
    Extract capitalized defined terms (common in credit agreements).
    """
    # Look for terms in quotes or fully capitalized multi-word terms
    quoted_terms = re.findall(r'"([^"]+)"', text)
    
    # Also look for capitalized terms (multiple consecutive capitalized words)
    cap_terms = re.findall(r'\b([A-Z][A-Z\s]+[A-Z])\b', text)
    
    all_terms = quoted_terms + cap_terms
    
    # Filter out common non-defined terms
    excluded = {'THE', 'AND', 'OR', 'TO', 'OF', 'IN', 'FOR', 'WITH', 'BY'}
    filtered_terms = [t for t in all_terms if t.upper() not in excluded]
    
    return list(set(filtered_terms))[:10]  # Limit to 10 most relevant
```

---

## Special Handling Requirements

### 1. Cross-References Preservation

Credit agreements heavily cross-reference other sections. Ensure cross-references are preserved:

```python
def add_cross_reference_context(chunks, all_chunks):
    """
    When a chunk references another section, add a preview of that section.
    """
    for chunk in chunks:
        references = chunk['metadata'].get('references', [])
        
        if references:
            # Find the referenced sections
            referenced_chunks = []
            for ref in references:
                for other_chunk in all_chunks:
                    if other_chunk['metadata'].get('section') == ref:
                        referenced_chunks.append(other_chunk)
                        break
            
            # Add abbreviated context
            if referenced_chunks:
                context = "\n\n--- REFERENCED SECTIONS ---\n"
                for ref_chunk in referenced_chunks[:2]:  # Limit to 2 references
                    context += f"\n{ref_chunk['metadata']['section']}: "
                    context += ref_chunk['text'][:200] + "...\n"
                
                chunk['text'] += context
    
    return chunks
```

### 2. Formula Preservation

Financial formulas must remain intact:

```python
def preserve_formulas(text):
    """
    Ensure financial formulas are not broken across chunks.
    """
    # Identify formula patterns
    formula_pattern = re.compile(
        r'(?:equals|=)\s*(?:\([^\)]+\)|\[[^\]]+\]|[^\n]{10,200})',
        re.IGNORECASE
    )
    
    formulas = list(formula_pattern.finditer(text))
    
    # Mark formula boundaries as "do not split here"
    protected_spans = []
    for formula in formulas:
        protected_spans.append((formula.start(), formula.end()))
    
    return protected_spans
```

### 3. Table Integrity

Tables must stay together:

```python
def identify_table_boundaries(text):
    """
    Identify where tables start and end to prevent splitting them.
    """
    # Look for table indicators
    table_start_patterns = [
        r'\n\s*\|',  # Markdown table
        r'Level\s+\|',  # Pricing grid
        r'Covenant\s+\|',  # Covenant matrix
    ]
    
    # Find table boundaries
    in_table = False
    table_spans = []
    current_start = None
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Check if line is part of a table
        is_table_line = '|' in line or (in_table and line.strip().startswith(('-', '=')))
        
        if is_table_line and not in_table:
            # Table starting
            in_table = True
            current_start = i
        elif not is_table_line and in_table:
            # Table ending
            in_table = False
            table_spans.append((current_start, i - 1))
    
    return table_spans
```

### 4. Compliance Certificate Specific Handling

Compliance certificates have a specific structure that should be preserved:

```python
def chunk_compliance_certificate(cert_text):
    """
    Chunk compliance certificate keeping each covenant calculation together.
    """
    chunks = []
    
    # Pattern to identify covenant calculations
    # Usually starts with covenant name and includes formula, calculation, result
    covenant_pattern = re.compile(
        r'(?:Covenant|Section)\s+\d+\.?\d*[:\s]+([^\n]+)\n',
        re.IGNORECASE
    )
    
    covenants = list(covenant_pattern.finditer(cert_text))
    
    for i, cov_match in enumerate(covenants):
        covenant_name = cov_match.group(1).strip()
        start_pos = cov_match.start()
        
        # Find end (start of next covenant or end of document)
        if i + 1 < len(covenants):
            end_pos = covenants[i + 1].start()
        else:
            end_pos = len(cert_text)
        
        covenant_section = cert_text[start_pos:end_pos]
        
        # Extract key information
        metadata = {
            'covenant_name': covenant_name,
            'type': 'compliance_calculation',
        }
        
        # Try to extract requirement and actual values
        req_match = re.search(r'(?:Required|Requirement):\s*([^\n]+)', covenant_section)
        actual_match = re.search(r'(?:Actual|As of):\s*([^\n]+)', covenant_section)
        
        if req_match:
            metadata['requirement'] = req_match.group(1).strip()
        if actual_match:
            metadata['actual_value'] = actual_match.group(1).strip()
        
        chunks.append({
            'text': covenant_section,
            'metadata': metadata
        })
    
    return chunks
```

---

## Implementation Examples

### Complete Preprocessing Pipeline

```python
class CreditDocumentPreprocessor:
    """
    Complete preprocessing pipeline for credit documents.
    """
    
    def __init__(self):
        self.chunker = CreditAgreementChunker()
    
    def process_document(self, file_path):
        """
        Main processing pipeline.
        """
        # Step 1: Load document
        print(f"Loading {file_path}...")
        if file_path.endswith('.pdf'):
            raw_content = self.load_pdf_with_structure(file_path)
        elif file_path.endswith('.docx'):
            raw_content = self.load_docx_with_structure(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Step 2: Identify document type
        doc_type = self.identify_document_type(raw_content)
        print(f"Document type: {doc_type}")
        
        # Step 3: Extract and clean text
        cleaned_text = self.clean_and_structure(raw_content)
        
        # Step 4: Chunk intelligently based on document type
        if doc_type == 'Credit Agreement':
            chunks = self.chunk_credit_agreement(cleaned_text)
        elif doc_type == 'Compliance Certificate':
            chunks = self.chunk_compliance_certificate(cleaned_text)
        else:
            chunks = self.chunk_generic(cleaned_text)
        
        # Step 5: Enhance metadata
        enhanced_chunks = self.enhance_chunks_metadata(
            chunks,
            file_path,
            doc_type
        )
        
        # Step 6: Add cross-reference context
        final_chunks = self.add_cross_reference_context(enhanced_chunks)
        
        print(f"Created {len(final_chunks)} chunks")
        
        return final_chunks
    
    def load_pdf_with_structure(self, file_path):
        """Load PDF preserving structure."""
        # Implementation from earlier
        pass
    
    def load_docx_with_structure(self, file_path):
        """Load DOCX preserving structure."""
        # Implementation from earlier
        pass
    
    def identify_document_type(self, content):
        """Identify document type."""
        # Implementation from earlier
        pass
    
    def clean_and_structure(self, raw_content):
        """Clean and structure text."""
        # Implementation from earlier
        pass
    
    def chunk_credit_agreement(self, text):
        """Chunk credit agreement."""
        return self.chunker.chunk_by_sections(text)
    
    def chunk_compliance_certificate(self, text):
        """Chunk compliance certificate."""
        return chunk_compliance_certificate(text)
    
    def chunk_generic(self, text):
        """Generic chunking."""
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150
        )
        
        return splitter.split_text(text)
    
    def enhance_chunks_metadata(self, chunks, file_path, doc_type):
        """Add metadata to chunks."""
        enhanced = []
        
        for i, chunk in enumerate(chunks):
            if isinstance(chunk, dict):
                chunk_text = chunk.get('text', chunk)
                existing_metadata = chunk.get('metadata', {})
            else:
                chunk_text = chunk
                existing_metadata = {}
            
            # Extract metadata
            metadata = extract_metadata(
                chunk_text,
                {
                    'filename': Path(file_path).name,
                    'type': doc_type,
                }
            )
            
            # Merge with existing metadata
            metadata.update(existing_metadata)
            metadata['chunk_id'] = i
            metadata['total_chunks'] = len(chunks)
            
            enhanced.append({
                'text': chunk_text,
                'metadata': metadata
            })
        
        return enhanced
    
    def add_cross_reference_context(self, chunks):
        """Add context for cross-references."""
        return add_cross_reference_context(chunks, chunks)
```

### Usage Example

```python
# Initialize preprocessor
preprocessor = CreditDocumentPreprocessor()

# Process a credit agreement
chunks = preprocessor.process_document('./documents/Senior_Credit_Agreement.pdf')

# Convert to LangChain documents
from langchain.schema import Document

langchain_docs = [
    Document(
        page_content=chunk['text'],
        metadata=chunk['metadata']
    )
    for chunk in chunks
]

# Now ready for embedding and vector store
```

---

## Quality Assurance

### Validation Checklist

After preprocessing, validate:

```python
def validate_chunks(chunks):
    """
    Validate that chunks are properly formed.
    """
    issues = []
    
    for i, chunk in enumerate(chunks):
        # Check 1: No empty chunks
        if not chunk['text'].strip():
            issues.append(f"Chunk {i}: Empty text")
        
        # Check 2: Metadata present
        if 'metadata' not in chunk or not chunk['metadata']:
            issues.append(f"Chunk {i}: Missing metadata")
        
        # Check 3: Size reasonable
        if len(chunk['text']) < 100:
            issues.append(f"Chunk {i}: Too small (<100 chars)")
        if len(chunk['text']) > 2000:
            issues.append(f"Chunk {i}: Too large (>2000 chars)")
        
        # Check 4: No broken sentences at boundaries
        if not chunk['text'][-1] in '.!?"':
            issues.append(f"Chunk {i}: May have broken sentence at end")
        
        # Check 5: Section information present for credit agreements
        if chunk['metadata'].get('document_type') == 'Credit Agreement':
            if 'section' not in chunk['metadata'] and 'article' not in chunk['metadata']:
                issues.append(f"Chunk {i}: Missing section/article info")
        
        # Check 6: Tables preserved
        if '|' in chunk['text']:
            # Count pipe characters per line - should be consistent in tables
            lines = chunk['text'].split('\n')
            pipe_counts = [line.count('|') for line in lines if '|' in line]
            if len(set(pipe_counts)) > 2:  # Allow for header separator
                issues.append(f"Chunk {i}: Table may be malformed")
    
    return issues
```

### Testing Retrieval Quality

```python
def test_retrieval_quality(vector_store, test_queries):
    """
    Test that preprocessing enables good retrieval.
    """
    results = {}
    
    for query, expected_section in test_queries:
        # Retrieve top 3 chunks
        docs = vector_store.similarity_search(query, k=3)
        
        # Check if expected section is in top 3
        found = any(
            expected_section in doc.metadata.get('section', '')
            for doc in docs
        )
        
        results[query] = {
            'found_expected': found,
            'top_sections': [
                doc.metadata.get('section', 'N/A')
                for doc in docs
            ]
        }
    
    return results

# Example test queries
test_queries = [
    ("What is the leverage ratio requirement?", "6.12"),
    ("What is EBITDA defined as?", "1.01"),
    ("What are the events of default?", "8.01"),
    ("What is the pricing grid?", "2.03"),
]

# Run tests
test_results = test_retrieval_quality(vector_store, test_queries)
```

---

## Best Practices Summary

### DO:
✅ Preserve section and article hierarchy  
✅ Keep tables intact  
✅ Include cross-reference context  
✅ Add rich metadata (section numbers, content types, financial markers)  
✅ Respect natural boundaries (sections, subsections)  
✅ Keep definitions complete  
✅ Preserve financial formulas  
✅ Use appropriate chunk sizes for different content types  
✅ Clean OCR errors and formatting issues  
✅ Validate chunks before indexing  

### DON'T:
❌ Split definitions across chunks  
❌ Break tables  
❌ Split formulas  
❌ Remove section numbers or headers  
❌ Use uniform chunk size for all content types  
❌ Ignore document structure  
❌ Skip metadata enhancement  
❌ Forget to preserve cross-references  
❌ Mix different document types without identification  
❌ Over-chunk (creating chunks that are too small)  

---

## Conclusion

Proper preprocessing and chunking of credit agreements is crucial for RAG system performance. By respecting document structure, preserving critical elements like formulas and tables, and enriching chunks with comprehensive metadata, you enable accurate retrieval and high-quality responses to credit analyst queries.

The strategies outlined in this guide have been optimized specifically for LSTA credit agreements and compliance certificates, but can be adapted for other financial documents with similar characteristics.
