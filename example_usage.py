"""
Example Usage Script for Credit Agreement Chatbot

This script demonstrates common query patterns and advanced usage scenarios
for analyzing credit agreements and compliance certificates.
"""

from credit_agreement_chatbot import CreditAgreementChatbot
import json
from datetime import datetime

def print_section(title):
    """Print formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_response(response):
    """Print formatted chatbot response."""
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
    
    print("\n" + "="*80)

# Initialize the chatbot
print_section("Initializing Credit Agreement Chatbot")
chatbot = CreditAgreementChatbot(
    documents_directory="./credit_documents",
    vector_store_path="./vector_store",
    model_name="gpt-3.5-turbo"  # Change to "gpt-4" for better quality
)

# Example 1: Basic Covenant Query
print_section("Example 1: Finding Covenant Information")
query1 = "What is the maximum leverage ratio covenant requirement?"
print(f"Query: {query1}\n")
response1 = chatbot.query(query1)
print_response(response1)

# Example 2: Definition Lookup
print_section("Example 2: Looking Up a Definition")
query2 = "How is EBITDA defined in the credit agreement?"
print(f"Query: {query2}\n")
response2 = chatbot.query(query2)
print_response(response2)

# Example 3: Covenant Compliance Check
print_section("Example 3: Checking Covenant Compliance")
query3 = "Are we in compliance with the leverage ratio covenant based on the latest compliance certificate?"
print(f"Query: {query3}\n")
response3 = chatbot.query(query3)
print_response(response3)

# Example 4: Pricing Information
print_section("Example 4: Querying Pricing Information")
query4 = "What is the pricing grid and what is our current applicable margin?"
print(f"Query: {query4}\n")
response4 = chatbot.query(query4)
print_response(response4)

# Example 5: Events of Default
print_section("Example 5: Events of Default")
query5 = "What are the events of default and are there any grace periods?"
print(f"Query: {query5}\n")
response5 = chatbot.query(query5)
print_response(response5)

# Example 6: Cross-Document Analysis
print_section("Example 6: Cross-Document Comparison")
query6 = "Compare the debt incurrence limitations in the credit agreement with our actual debt levels in the compliance certificate"
print(f"Query: {query6}\n")
response6 = chatbot.query(query6)
print_response(response6)

# Example 7: Financial Covenant Calculation
print_section("Example 7: Understanding Covenant Calculations")
query7 = "How is the Fixed Charge Coverage Ratio calculated and what add-backs are allowed?"
print(f"Query: {query7}\n")
response7 = chatbot.query(query7)
print_response(response7)

# Example 8: Negative Covenant with Exceptions
print_section("Example 8: Negative Covenant Exceptions")
query8 = "What investments are permitted under the limitations on investments covenant?"
print(f"Query: {query8}\n")
response8 = chatbot.query(query8)
print_response(response8)

# Example 9: Fee Structure
print_section("Example 9: Fee Information")
query9 = "What fees are we required to pay and when are they due?"
print(f"Query: {query9}\n")
response9 = chatbot.query(query9)
print_response(response9)

# Example 10: Maturity and Amortization
print_section("Example 10: Loan Terms")
query10 = "What is the maturity date of the credit facility and are there any mandatory prepayments?"
print(f"Query: {query10}\n")
response10 = chatbot.query(query10)
print_response(response10)

# Advanced Usage Example: Programmatic Analysis
print_section("Advanced: Programmatic Covenant Analysis")

# List of covenants to check
covenants_to_check = [
    "Total Leverage Ratio",
    "Senior Secured Leverage Ratio",
    "Fixed Charge Coverage Ratio",
    "Minimum Liquidity"
]

covenant_results = []

for covenant in covenants_to_check:
    print(f"\nAnalyzing {covenant}...")
    
    query = f"What is the {covenant} requirement and are we in compliance based on the latest compliance certificate?"
    response = chatbot.query(query)
    
    covenant_results.append({
        "covenant": covenant,
        "answer": response["answer"],
        "sources": len(response["sources"]),
        "timestamp": response["timestamp"]
    })

# Print summary
print("\n" + "-"*80)
print("COVENANT COMPLIANCE SUMMARY")
print("-"*80)

for result in covenant_results:
    print(f"\n{result['covenant']}:")
    print(f"  Sources consulted: {result['sources']}")
    print(f"  {result['answer'][:200]}...")  # First 200 chars

# Export results to JSON
print("\n" + "-"*80)
print("Exporting results to covenant_analysis.json...")

with open("covenant_analysis.json", "w") as f:
    json.dump(covenant_results, f, indent=2)

print("✓ Export complete!")

# Example of manual refresh
print_section("Advanced: Manual Document Refresh")
print("If you've added new documents, you can manually refresh:")
print("chatbot.manual_refresh()")
print("\nThis will re-index all documents in the directory.")

# Best Practices Section
print_section("Best Practices for Queries")

best_practices = """
1. BE SPECIFIC
   ❌ "Tell me about covenants"
   ✓ "What is the maximum leverage ratio covenant requirement?"

2. REQUEST COMPARISONS EXPLICITLY
   ❌ "Check our debt"
   ✓ "Compare our total debt in the compliance certificate with the debt limitations in the credit agreement"

3. ASK FOR SPECIFIC SECTIONS
   ❌ "What are the fees?"
   ✓ "What is the commitment fee rate and how is it calculated?"

4. REQUEST TABLES FOR COMPARISONS
   ❌ "Are we compliant with all covenants?"
   ✓ "Show me a table comparing all financial covenant requirements with our actual performance"

5. ASK FOLLOW-UP QUESTIONS
   First query: "What is the pricing grid?"
   Follow-up: "Based on our current leverage ratio, what pricing level applies?"

6. REQUEST CONFIDENCE LEVELS
   Add to any query: "...and indicate your confidence level"

7. ASK FOR CITATIONS
   The system automatically provides citations, but you can request more detail:
   "Which specific section of the credit agreement defines EBITDA?"

8. USE NATURAL LANGUAGE
   The system understands conversational queries:
   "We're thinking about incurring more debt - what's the maximum we can incur?"
"""

print(best_practices)

# Performance Tips
print_section("Performance Optimization Tips")

performance_tips = """
1. DOCUMENT ORGANIZATION
   - Keep document names clear and consistent
   - Remove old/superseded versions to reduce index size
   - Ensure documents are text-searchable (not scanned images)

2. QUERY OPTIMIZATION
   - More specific queries return better results
   - Include relevant timeframes (e.g., "Q3 2024")
   - Reference document types when known (e.g., "in the compliance certificate")

3. SYSTEM CONFIGURATION
   - Use GPT-4 for complex analysis requiring high accuracy
   - Use GPT-3.5-turbo for faster responses on simple queries
   - Adjust chunk_size for your specific document structure

4. REFRESH STRATEGY
   - Default hourly refresh is suitable for most use cases
   - Use manual refresh immediately after adding critical documents
   - Consider reducing refresh interval during active covenant testing periods

5. MONITORING
   - Review source citations to ensure relevant retrieval
   - Check confidence levels in responses
   - Report queries with poor results to improve the system
"""

print(performance_tips)

print_section("Script Complete")
print("This script demonstrated:")
print("✓ 10 common query patterns")
print("✓ Programmatic covenant analysis")
print("✓ JSON export capability")
print("✓ Best practices and optimization tips")
print("\nRefer to the README.md for more detailed documentation.")
print("="*80 + "\n")
