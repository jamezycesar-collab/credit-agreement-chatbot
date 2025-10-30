# Credit Agreement Analysis Chatbot - RAG Implementation

A specialized RAG (Retrieval-Augmented Generation) chatbot built with LangChain for analyzing LSTA credit agreements, credit applications, and compliance certificates. This system helps credit analysts quickly access and compare information across multiple financial documents.

## Features

- **Automatic Document Monitoring**: Hourly refresh to detect new documents
- **Intelligent Chunking**: Preserves document structure, definitions, and covenants
- **Cross-Document Analysis**: Compares covenant requirements with compliance data
- **Source Citations**: Every answer includes document name and section references
- **Covenant Comparison Tables**: Formatted tables for covenant compliance analysis
- **Financial Term Highlighting**: Automatic highlighting of amounts, dates, and percentages
- **Confidence Levels**: Indicates certainty of information retrieval
- **Expert Domain Knowledge**: Specialized in LSTA credit agreement terminology

## Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (for GPT models)
- 2GB+ free disk space for vector store
- 4GB+ RAM recommended

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Create documents directory**
```bash
mkdir credit_documents
```

5. **Add your documents**

Place your credit agreements, compliance certificates, and credit applications in the `credit_documents` folder. Supported formats:
- PDF (`.pdf`)
- Word Documents (`.docx`)

### Running the Chatbot

**Basic usage:**
```bash
python credit_agreement_chatbot.py
```

**With custom configuration:**
```python
from credit_agreement_chatbot import CreditAgreementChatbot

chatbot = CreditAgreementChatbot(
    documents_directory="./credit_documents",
    vector_store_path="./vector_store",
    model_name="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
    refresh_interval=3600  # 1 hour in seconds
)

# Query the chatbot
response = chatbot.query("What is the leverage ratio requirement?")
print(response['answer'])
```

## Usage Examples

### Example 1: Finding Covenant Information
```
Your Question: What is the maximum leverage ratio covenant?

ANSWER:
Based on the **Senior Credit Agreement dated March 15, 2024, Section 6.12(a)**, 
the Maximum Total Leverage Ratio covenant requires:

- **Q1-Q2 2024:** ≤ **4.50:1.00**
- **Q3-Q4 2024:** ≤ **4.25:1.00**
- **Q1 2025 onwards:** ≤ **4.00:1.00**

Confidence Level: I can confirm this information directly from the credit agreement.
```

### Example 2: Covenant Compliance Check
```
Your Question: Are we in compliance with the leverage ratio covenant?

ANSWER:
According to the **Compliance Certificate dated June 30, 2024**, your actual 
Total Leverage Ratio was **3.85:1.00**.

| Covenant | Requirement | Actual | Status |
|----------|-------------|--------|--------|
| Total Leverage Ratio | ≤ 4.50:1.00 | 3.85:1.00 | ✓ Pass |

You are in compliance with a cushion of **0.65**.

Confidence Level: I can confirm this based on [Credit Agreement, Section 6.12(a)] 
and [Compliance Certificate dated 06/30/2024].
```

### Example 3: Cross-Document Analysis
```
Your Question: Compare our debt levels in the compliance certificate with what's 
allowed in the credit agreement

ANSWER:
Based on cross-document analysis:

**From Credit Agreement (Section 7.02 - Limitation on Indebtedness)**:
Maximum permitted debt: **$50,000,000** plus permitted baskets

**From Compliance Certificate (dated September 30, 2024)**:
Actual Total Debt: **$42,500,000**

| Debt Type | Limit | Actual | Available Capacity |
|-----------|-------|--------|-------------------|
| Total Debt | $50M | $42.5M | $7.5M |

Status: ✓ IN COMPLIANCE

Confidence Level: I can confirm these figures from [Credit Agreement, Section 7.02, 
Page 48] and [Compliance Certificate Q3 2024, Page 3].
```

## Document Structure Requirements

### Supported Document Types

1. **LSTA Credit Agreements**
   - Standard article/section structure
   - Definitions (Article I)
   - Covenants (Articles VI-VII)
   - Events of Default (Article VIII)
   - Pricing grids and schedules

2. **Compliance Certificates**
   - Covenant calculations
   - Financial statement data
   - Officer certifications

3. **Credit Applications**
   - Borrower information
   - Financial projections
   - Use of proceeds

### Optimal Document Preparation

For best results:
- Ensure documents are text-searchable (not scanned images)
- Include complete section numbers in headers
- Keep pricing grids and tables formatted clearly
- Use consistent date formats (MM/DD/YYYY)

See `document_preprocessing_guide.md` for detailed preprocessing strategies.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Query                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              CreditAgreementChatbot                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Check if hourly refresh needed                   │  │
│  │  2. Query classification (optional)                  │  │
│  │  3. Retrieve relevant chunks from vector store       │  │
│  │  4. Apply specialized prompt template                │  │
│  │  5. Generate response with LLM                       │  │
│  │  6. Format with citations and confidence level       │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌─────────────┐
│ Vector Store │ │ Embeddings  │ │     LLM     │
│   (FAISS)    │ │  (HF Model) │ │  (GPT-3.5/4)│
└──────────────┘ └─────────────┘ └─────────────┘
        │
        │ Hourly Refresh
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│               Document Directory                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Credit_Agreement_2024.pdf                         │  │
│  │  • Compliance_Cert_Q3_2024.pdf                       │  │
│  │  • Credit_Application.docx                           │  │
│  │  • ...                                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Options

### Embedding Models

**Default**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, fast)

**Alternatives**:
- `sentence-transformers/all-mpnet-base-v2` (768 dimensions, higher quality)
- `BAAI/bge-large-en-v1.5` (1024 dimensions, best quality)

```python
chatbot = CreditAgreementChatbot(
    embedding_model="sentence-transformers/all-mpnet-base-v2"
)
```

### LLM Models

**Default**: `gpt-3.5-turbo` (fast, cost-effective)

**Recommended for production**: `gpt-4` or `gpt-4-turbo` (higher accuracy)

```python
chatbot = CreditAgreementChatbot(
    model_name="gpt-4"
)
```

### Chunk Size Configuration

Default settings are optimized for credit agreements, but can be adjusted:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

custom_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Larger chunks for more context
    chunk_overlap=250,  # More overlap for better continuity
)
```

### Refresh Interval

**Default**: 3600 seconds (1 hour)

```python
chatbot = CreditAgreementChatbot(
    refresh_interval=1800  # 30 minutes
)
```

## Specialized Retrieval Prompts

The system includes pre-built prompts for extracting specific information:

- **Covenant Extraction**: Financial and negative covenants
- **Definition Lookup**: Defined terms and financial metrics
- **Pricing Information**: Interest rates and fee structures
- **Events of Default**: Default triggers and remedies
- **Compliance Verification**: Cross-document compliance checks

See `specialized_retrieval_prompts.md` for detailed prompt templates.

## Advanced Features

### Manual Document Refresh

If you've added new documents and don't want to wait for the hourly refresh:

```python
chatbot.manual_refresh()
```

Or via command line:
```
Your Question: refresh
```

### Accessing Source Documents

Every response includes source information:

```python
response = chatbot.query("What is EBITDA?")

# Access the answer
print(response['answer'])

# Access source documents
for source in response['sources']:
    print(f"File: {source['filename']}")
    print(f"Page: {source['page']}")
    print(f"Section: {source['section']}")
    print(f"Preview: {source['content_preview']}")
```

### Custom Prompts

Modify the system prompt for specific use cases:

```python
custom_prompt = """You are a specialized credit analyst assistant...
[Your custom instructions here]
"""

# Update the QA chain with custom prompt
# (requires modifying the _initialize_qa_chain method)
```

## Performance Optimization

### For Large Document Sets (>20 documents)

1. **Use GPU embeddings** if available:
```bash
pip install faiss-gpu
```

2. **Switch to more scalable vector stores**:
```bash
pip install chromadb
# or
pip install pinecone-client
```

3. **Implement caching**:
```bash
pip install redis
```

### For Faster Responses

1. **Reduce retrieval count**:
```python
# In _initialize_qa_chain, modify:
search_kwargs={"k": 3}  # Instead of 6
```

2. **Use smaller embedding model**:
```python
embedding_model="sentence-transformers/all-MiniLM-L6-v2"
```

3. **Use GPT-3.5-turbo** instead of GPT-4

## Troubleshooting

### Issue: "No documents found to index"
**Solution**: Verify documents are in the correct directory and format (PDF or DOCX)

### Issue: "Out of memory"
**Solution**: 
- Reduce chunk size
- Process documents in batches
- Use CPU-based FAISS instead of loading all into memory

### Issue: "Rate limit exceeded" (OpenAI)
**Solution**:
- Add rate limiting to queries
- Use exponential backoff
- Upgrade OpenAI plan

### Issue: Poor retrieval quality
**Solution**:
- Review preprocessing with `document_preprocessing_guide.md`
- Increase chunk overlap
- Use better embedding model
- Add more metadata to chunks

### Issue: Slow document refresh
**Solution**:
- Use multithreading for document loading
- Cache unchanged documents
- Reduce refresh frequency

## Security Considerations

1. **API Keys**: Never commit `.env` file to version control
2. **Document Access**: Ensure proper access controls on document directory
3. **Sensitive Data**: Credit agreements contain confidential financial information
4. **Compliance**: Ensure usage complies with data handling regulations

## Deployment Options

### Local Deployment
Current implementation runs locally - suitable for development and small teams.

### API Deployment
Deploy as FastAPI service:

```python
# api.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
chatbot = CreditAgreementChatbot(...)

class Query(BaseModel):
    question: str

@app.post("/query")
async def query_endpoint(query: Query):
    response = chatbot.query(query.question)
    return response
```

Run with:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Cloud Deployment
- **AWS**: Deploy on EC2 or Lambda with EFS for document storage
- **Azure**: Use Azure Functions with Blob Storage
- **GCP**: Deploy on Cloud Run with Cloud Storage

## Cost Estimation

### Per Query Costs (approximate)

**Embeddings** (one-time per document):
- Local HuggingFace models: **Free**

**LLM Costs** (per query):
- GPT-3.5-turbo: ~$0.002 per query
- GPT-4: ~$0.03 per query

**Storage**:
- Vector store: Negligible (local storage)
- Pinecone (if used): ~$70/month for 100k vectors

### Monthly Cost Examples

**Small team (100 queries/day)**:
- GPT-3.5-turbo: ~$6/month
- GPT-4: ~$90/month

**Medium usage (500 queries/day)**:
- GPT-3.5-turbo: ~$30/month
- GPT-4: ~$450/month

## Contributing

To extend or improve the system:

1. **Add new document types**: Modify `_identify_document_type()`
2. **Enhance chunking**: Update `CreditAgreementChunker` class
3. **Add new prompts**: Expand `specialized_retrieval_prompts.md`
4. **Improve metadata**: Extend `extract_metadata()` function

## Resources

- **Documentation**: See `specialized_retrieval_prompts.md` and `document_preprocessing_guide.md`
- **LangChain Docs**: https://python.langchain.com/docs/
- **OpenAI API**: https://platform.openai.com/docs/
- **LSTA**: https://www.lsta.org/

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the preprocessing guide
3. Consult LangChain documentation
4. Open an issue with detailed error messages and logs

---

**Version**: 1.0.0  
**Last Updated**: 2025  
**Tested With**: Python 3.9+, LangChain 0.1.0, OpenAI API
