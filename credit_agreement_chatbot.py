"""
Credit Agreement Analysis Chatbot - RAG Implementation
A LangChain-based chatbot for analyzing LSTA credit agreements, credit applications, 
and compliance certificates.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CreditAgreementChatbot:
    """
    RAG-based chatbot for analyzing credit agreements and compliance documents.
    """
    
    def __init__(
        self,
        documents_directory: str,
        vector_store_path: str = "./vector_store",
        model_name: str = "gpt-3.5-turbo",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        refresh_interval: int = 3600  # 1 hour in seconds
    ):
        """
        Initialize the Credit Agreement Chatbot.
        
        Args:
            documents_directory: Path to directory containing credit documents
            vector_store_path: Path to store/load the vector database
            model_name: OpenAI model name for the LLM
            embedding_model: HuggingFace embedding model name
            refresh_interval: Time in seconds between document refresh (default 1 hour)
        """
        self.documents_directory = Path(documents_directory)
        self.vector_store_path = Path(vector_store_path)
        self.model_name = model_name
        self.refresh_interval = refresh_interval
        self.last_refresh = None
        
        # Initialize embeddings
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize text splitter with credit-specific configuration
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            length_function=len,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                "SECTION",  # Common in credit agreements
                "Section",
                "ARTICLE",
                "Article",
                ". ",    # Sentence breaks
                " ",     # Word breaks
                ""
            ]
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0,  # Deterministic responses for financial analysis
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        # Initialize vector store
        self.vector_store = None
        self.qa_chain = None
        
        # Load or create initial vector store
        self._initialize_vector_store()
        
    def _initialize_vector_store(self):
        """Initialize or load existing vector store."""
        if self.vector_store_path.exists() and (self.vector_store_path / "index.faiss").exists():
            logger.info("Loading existing vector store...")
            try:
                self.vector_store = FAISS.load_local(
                    str(self.vector_store_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.last_refresh = datetime.now()
                logger.info("Vector store loaded successfully")
            except Exception as e:
                logger.error(f"Error loading vector store: {e}")
                logger.info("Creating new vector store...")
                self._refresh_documents()
        else:
            logger.info("No existing vector store found. Creating new one...")
            self._refresh_documents()
            
        # Initialize QA chain
        self._initialize_qa_chain()
    
    def _load_documents(self) -> List[Document]:
        """
        Load all documents from the directory.
        
        Returns:
            List of loaded documents with metadata
        """
        logger.info(f"Loading documents from {self.documents_directory}")
        documents = []
        
        # Load PDFs
        pdf_loader = DirectoryLoader(
            str(self.documents_directory),
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True
        )
        
        # Load Word documents
        docx_loader = DirectoryLoader(
            str(self.documents_directory),
            glob="**/*.docx",
            loader_cls=Docx2txtLoader,
            show_progress=True
        )
        
        try:
            pdf_docs = pdf_loader.load()
            docx_docs = docx_loader.load()
            documents.extend(pdf_docs)
            documents.extend(docx_docs)
            
            # Enhance metadata
            for doc in documents:
                if 'source' in doc.metadata:
                    doc.metadata['filename'] = Path(doc.metadata['source']).name
                    doc.metadata['file_type'] = Path(doc.metadata['source']).suffix
                    
            logger.info(f"Loaded {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return []
    
    def _preprocess_documents(self, documents: List[Document]) -> List[Document]:
        """
        Preprocess and chunk documents for optimal retrieval.
        
        Args:
            documents: List of raw documents
            
        Returns:
            List of chunked documents with enhanced metadata
        """
        logger.info("Preprocessing and chunking documents...")
        
        processed_docs = []
        
        for doc in documents:
            # Clean the text
            text = doc.page_content
            
            # Add document-level metadata to help with citations
            filename = doc.metadata.get('filename', 'Unknown')
            
            # Identify document type based on content
            doc_type = self._identify_document_type(text)
            doc.metadata['document_type'] = doc_type
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Enhance chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_id'] = i
                chunk.metadata['total_chunks'] = len(chunks)
                
                # Try to identify section information
                section_info = self._extract_section_info(chunk.page_content)
                if section_info:
                    chunk.metadata['section'] = section_info
                    
                processed_docs.append(chunk)
        
        logger.info(f"Created {len(processed_docs)} chunks from {len(documents)} documents")
        return processed_docs
    
    def _identify_document_type(self, text: str) -> str:
        """
        Identify the type of credit document.
        
        Args:
            text: Document text content
            
        Returns:
            Document type string
        """
        text_lower = text.lower()
        
        if 'compliance certificate' in text_lower:
            return 'Compliance Certificate'
        elif 'credit agreement' in text_lower or 'loan agreement' in text_lower:
            return 'Credit Agreement'
        elif 'credit application' in text_lower:
            return 'Credit Application'
        elif 'lsta' in text_lower:
            return 'LSTA Agreement'
        else:
            return 'Credit Document'
    
    def _extract_section_info(self, text: str) -> Optional[str]:
        """
        Extract section or article information from chunk text.
        
        Args:
            text: Chunk text content
            
        Returns:
            Section identifier or None
        """
        import re
        
        # Look for common section patterns
        patterns = [
            r'SECTION\s+(\d+\.?\d*)',
            r'Section\s+(\d+\.?\d*)',
            r'ARTICLE\s+([IVXLCDM]+|\d+)',
            r'Article\s+([IVXLCDM]+|\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:500])  # Check first 500 chars
            if match:
                return match.group(0)
        
        return None
    
    def _refresh_documents(self):
        """Refresh the vector store with current documents."""
        logger.info("Refreshing document index...")
        
        # Load documents
        documents = self._load_documents()
        
        if not documents:
            logger.warning("No documents found to index")
            return
        
        # Preprocess documents
        processed_docs = self._preprocess_documents(documents)
        
        # Create new vector store
        logger.info("Creating vector store...")
        self.vector_store = FAISS.from_documents(
            processed_docs,
            self.embeddings
        )
        
        # Save vector store
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(self.vector_store_path))
        
        self.last_refresh = datetime.now()
        logger.info(f"Vector store refreshed at {self.last_refresh}")
    
    def _check_and_refresh(self):
        """Check if refresh is needed and perform it."""
        if self.last_refresh is None:
            self._refresh_documents()
            return
        
        time_since_refresh = (datetime.now() - self.last_refresh).total_seconds()
        
        if time_since_refresh >= self.refresh_interval:
            logger.info("Refresh interval reached. Updating document index...")
            self._refresh_documents()
            # Reinitialize QA chain with new vector store
            self._initialize_qa_chain()
    
    def _initialize_qa_chain(self):
        """Initialize the QA chain with custom prompt."""
        
        # Custom prompt template for credit analysis
        prompt_template = """You are an expert credit analyst assistant specializing in LSTA credit agreements, credit applications, and compliance certificates.

Your task is to answer questions about credit documents with precision and proper citations.

IMPORTANT RULES:
1. ALWAYS cite the specific document name and section/page reference
2. Format citations as: [Document Name, Section X.X] or [Document Name, Page X]
3. Highlight financial terms (dollar amounts, percentages, ratios) using **bold**
4. Highlight dates and time periods using **bold**
5. Indicate confidence level: "I can confirm...", "It appears...", "I found partial information...", or "I cannot find that in the documents available."
6. If information is not in the documents, clearly state: "I cannot find that in the documents available."
7. When comparing covenants, use table format
8. If the query is ambiguous, ask clarifying questions
9. Maintain a professional, formal tone

Context from documents:
{context}

Question: {question}

Provide a detailed answer with proper citations, confidence level, and formatting:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 6}  # Retrieve top 6 most relevant chunks
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        logger.info("QA chain initialized")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the chatbot with a question.
        
        Args:
            question: User's question about credit documents
            
        Returns:
            Dictionary containing answer and source documents
        """
        # Check if refresh is needed
        self._check_and_refresh()
        
        logger.info(f"Processing query: {question}")
        
        try:
            result = self.qa_chain({"query": question})
            
            # Format the response
            response = {
                "answer": result["result"],
                "sources": [
                    {
                        "filename": doc.metadata.get("filename", "Unknown"),
                        "page": doc.metadata.get("page", "N/A"),
                        "section": doc.metadata.get("section", "N/A"),
                        "document_type": doc.metadata.get("document_type", "Unknown"),
                        "content_preview": doc.page_content[:200] + "..."
                    }
                    for doc in result["source_documents"]
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"I encountered an error processing your question: {str(e)}",
                "sources": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def manual_refresh(self):
        """Manually trigger a document refresh."""
        logger.info("Manual refresh triggered")
        self._refresh_documents()
        self._initialize_qa_chain()


def main():
    """
    Main function to run the chatbot.
    """
    # Configuration
    DOCUMENTS_DIR = "./credit_documents"  # Change to your directory
    VECTOR_STORE_PATH = "./vector_store"
    
    # Initialize chatbot
    print("Initializing Credit Agreement Chatbot...")
    chatbot = CreditAgreementChatbot(
        documents_directory=DOCUMENTS_DIR,
        vector_store_path=VECTOR_STORE_PATH
    )
    
    print("\n" + "="*80)
    print("Credit Agreement Analysis Chatbot")
    print("="*80)
    print("Ask questions about your credit agreements, applications, and compliance certificates.")
    print("Type 'refresh' to manually refresh the document index.")
    print("Type 'quit' or 'exit' to end the session.")
    print("="*80 + "\n")
    
    # Chat loop
    while True:
        try:
            question = input("\nYour Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit']:
                print("\nThank you for using Credit Agreement Chatbot. Goodbye!")
                break
            
            if question.lower() == 'refresh':
                print("\nRefreshing document index...")
                chatbot.manual_refresh()
                print("Document index refreshed successfully!")
                continue
            
            # Process query
            print("\nAnalyzing documents...\n")
            response = chatbot.query(question)
            
            print("\n" + "-"*80)
            print("ANSWER:")
            print("-"*80)
            print(response["answer"])
            
            print("\n" + "-"*80)
            print("SOURCES:")
            print("-"*80)
            for i, source in enumerate(response["sources"], 1):
                print(f"\n{i}. {source['filename']}")
                print(f"   Type: {source['document_type']}")
                print(f"   Page: {source['page']} | Section: {source['section']}")
                print(f"   Preview: {source['content_preview']}")
            
            print("\n" + "="*80)
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
