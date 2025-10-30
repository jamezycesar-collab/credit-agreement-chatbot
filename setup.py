#!/usr/bin/env python3
"""
Setup script for Credit Agreement Chatbot
Initializes directories, validates dependencies, and prepares the environment.
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_success(text):
    """Print success message."""
    print(f"✓ {text}")

def print_error(text):
    """Print error message."""
    print(f"✗ {text}")

def print_warning(text):
    """Print warning message."""
    print(f"⚠ {text}")

def check_python_version():
    """Check if Python version is adequate."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} detected")
        print("Python 3.9 or higher is required")
        return False

def create_directories():
    """Create necessary directories."""
    print_header("Creating Directories")
    
    directories = [
        "credit_documents",
        "vector_store",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {directory}")
        else:
            print_success(f"Directory already exists: {directory}")
    
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print_header("Checking Dependencies")
    
    required_packages = {
        'langchain': 'langchain',
        'openai': 'openai',
        'faiss': 'faiss-cpu',
        'sentence_transformers': 'sentence-transformers',
        'pypdf': 'pypdf',
        'pdfplumber': 'pdfplumber',
        'docx2txt': 'docx2txt',
        'docx': 'python-docx',
        'tiktoken': 'tiktoken',
        'dotenv': 'python-dotenv',
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print_success(f"{pip_name} is installed")
        except ImportError:
            print_error(f"{pip_name} is NOT installed")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("\n" + "-"*70)
        print("Missing packages detected. Install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        print("\nOr install all requirements:")
        print("pip install -r requirements.txt")
        print("-"*70)
        return False
    
    return True

def setup_env_file():
    """Setup .env file from template."""
    print_header("Setting up Environment File")
    
    env_path = Path(".env")
    template_path = Path(".env.template")
    
    if env_path.exists():
        print_warning(".env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return True
    
    if template_path.exists():
        # Copy template to .env
        with open(template_path, 'r') as template:
            content = template.read()
        
        with open(env_path, 'w') as env_file:
            env_file.write(content)
        
        print_success("Created .env file from template")
        print_warning("IMPORTANT: Edit .env file and add your OpenAI API key!")
        return True
    else:
        print_error(".env.template not found")
        return False

def check_openai_key():
    """Check if OpenAI API key is configured."""
    print_header("Checking OpenAI API Key")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here':
        print_error("OpenAI API key not configured")
        print("\nTo configure your API key:")
        print("1. Get your API key from: https://platform.openai.com/api-keys")
        print("2. Edit .env file and replace 'your_openai_api_key_here' with your actual key")
        return False
    else:
        print_success("OpenAI API key is configured")
        return True

def create_sample_documents_readme():
    """Create a README in the documents directory."""
    print_header("Creating Documents Directory README")
    
    readme_path = Path("credit_documents/README.md")
    
    if readme_path.exists():
        print_success("README already exists in credit_documents")
        return True
    
    readme_content = """# Credit Documents Directory

Place your credit agreement documents here for analysis.

## Supported File Types
- PDF files (.pdf)
- Word documents (.docx)

## Document Types
The chatbot is optimized for:
- LSTA Credit Agreements
- Compliance Certificates
- Credit Applications

## File Naming Suggestions
For better organization, consider naming your files:
- `CreditAgreement_[Company]_[Date].pdf`
- `ComplianceCert_[Company]_[Quarter]_[Year].pdf`
- `CreditApplication_[Company]_[Date].docx`

## Document Requirements
- Documents should be text-searchable (not scanned images)
- Include complete section numbers and headers
- Tables and pricing grids should be clearly formatted

## Automatic Detection
The system automatically detects new documents added to this directory every hour.
You can also trigger a manual refresh by typing 'refresh' in the chatbot.

## Privacy Note
These documents contain confidential financial information. Ensure proper access 
controls are in place and comply with your organization's data handling policies.
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print_success("Created README in credit_documents directory")
    return True

def test_basic_functionality():
    """Test basic system functionality."""
    print_header("Testing Basic Functionality")
    
    try:
        # Test embedding model loading
        print("Testing embedding model...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        test_embedding = model.encode(["test sentence"])
        print_success("Embedding model works correctly")
        
        # Test FAISS
        print("Testing FAISS vector store...")
        import faiss
        index = faiss.IndexFlatL2(384)  # MiniLM dimension
        print_success("FAISS vector store works correctly")
        
        return True
    except Exception as e:
        print_error(f"Functionality test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print_header("Setup Complete!")
    
    print("Next Steps:\n")
    print("1. Configure OpenAI API Key:")
    print("   - Edit the .env file")
    print("   - Add your OpenAI API key")
    print("   - Get a key from: https://platform.openai.com/api-keys\n")
    
    print("2. Add Your Documents:")
    print("   - Place PDF and DOCX files in the credit_documents/ directory")
    print("   - See credit_documents/README.md for guidelines\n")
    
    print("3. Run the Chatbot:")
    print("   python credit_agreement_chatbot.py\n")
    
    print("4. Read the Documentation:")
    print("   - README.md - Complete usage guide")
    print("   - specialized_retrieval_prompts.md - Prompt templates")
    print("   - document_preprocessing_guide.md - Preprocessing strategies\n")
    
    print("="*70)

def main():
    """Main setup function."""
    print_header("Credit Agreement Chatbot - Setup")
    
    print("This script will set up your environment for the Credit Agreement Chatbot.\n")
    
    all_checks_passed = True
    
    # Run all setup steps
    if not check_python_version():
        all_checks_passed = False
    
    if not create_directories():
        all_checks_passed = False
    
    if not check_dependencies():
        all_checks_passed = False
        print("\nPlease install missing dependencies and run setup again.")
        sys.exit(1)
    
    if not setup_env_file():
        all_checks_passed = False
    
    if not check_openai_key():
        all_checks_passed = False
    
    if not create_sample_documents_readme():
        all_checks_passed = False
    
    if all_checks_passed:
        if not test_basic_functionality():
            all_checks_passed = False
    
    print("\n" + "="*70)
    
    if all_checks_passed:
        print("✓ All checks passed!")
        print_next_steps()
    else:
        print("⚠ Some checks failed. Please review the errors above.")
        print("\nCommon issues:")
        print("- Missing dependencies: Run 'pip install -r requirements.txt'")
        print("- Missing API key: Edit .env and add your OpenAI API key")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
