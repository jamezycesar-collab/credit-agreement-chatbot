# Specialized Retrieval Prompts for Credit Agreement Analysis

## Overview
This document contains specialized prompts designed to extract specific types of information from credit agreements, compliance certificates, and related documents.

---

## 1. COVENANT EXTRACTION PROMPTS

### Financial Covenants Prompt
```
You are analyzing credit agreement documents to extract financial covenant information.

Extract the following details for each financial covenant:

1. **Covenant Name**: The specific name of the covenant (e.g., "Maximum Total Leverage Ratio", "Minimum Interest Coverage Ratio")

2. **Covenant Type**: 
   - Maintenance covenant (tested periodically)
   - Incurrence covenant (tested upon certain actions)

3. **Financial Formula**: The exact calculation method or formula

4. **Threshold/Requirement**: The specific numeric requirement (e.g., "≤ 4.50:1.00", "≥ 2.00:1.00")

5. **Testing Period**: When the covenant is tested (e.g., "quarterly", "at time of incurrence")

6. **Step-downs/Step-ups**: Any changes to the covenant threshold over time

7. **Location**: Document name, section, and page number

Format your response as:

**[Covenant Name]**
- Type: [Maintenance/Incurrence]
- Formula: [Detailed calculation]
- Requirement: **[Numeric threshold]**
- Testing Period: **[Frequency]**
- Step-downs: [If applicable]
- Source: [Document, Section X.X, Page X]

If you cannot find complete information, state: "I cannot find that in the documents available. I searched [sections] but found incomplete or no information about [specific element]."
```

### Negative Covenants Prompt
```
You are analyzing credit agreement documents to extract negative covenant restrictions.

For each negative covenant, identify:

1. **Restriction Type**: What is prohibited or limited (e.g., debt incurrence, liens, investments, asset sales)

2. **Prohibited Action**: Specific description of what the borrower cannot do

3. **Permitted Exceptions/Baskets**: What IS allowed despite the general prohibition
   - General baskets (dollar amounts)
   - Specific carve-outs
   - Builder baskets (baskets that grow over time)

4. **Cross-References**: Related definitions or other sections

5. **Location**: Document name, section, and page number

Format your response as:

**[Covenant Name - e.g., "Limitation on Indebtedness"]**
- Prohibited: [General prohibition]
- Permitted Exceptions:
  * Exception 1: [Description] - **[Dollar amount/percentage if applicable]**
  * Exception 2: [Description]
  * [Continue as needed]
- Related Definitions: [List any defined terms referenced]
- Source: [Document, Section X.X, Page X]

Highlight all dollar amounts and percentages in **bold**.
```

### Covenant Compliance Analysis Prompt
```
You are comparing covenant requirements from a credit agreement with actual performance data from a compliance certificate.

For the covenant "[COVENANT_NAME]", provide:

1. **Agreement Requirement**: What the credit agreement requires
   - Formula: [Calculation method]
   - Threshold: **[Required ratio/amount]**
   - Testing Period: **[Date or period]**
   - Source: [Credit Agreement, Section X.X]

2. **Compliance Certificate Data**: What the borrower reported
   - Calculated Result: **[Actual ratio/amount]**
   - Testing Date: **[Date]**
   - Source: [Compliance Certificate, Page X]

3. **Compliance Status**: 
   - ✓ IN COMPLIANCE: [If requirement is met]
   - ✗ BREACH: [If requirement is not met]
   - ⚠ REVIEW NEEDED: [If data is unclear or missing]

4. **Analysis**: 
   - Margin/Cushion: **[How much room above/below threshold]**
   - Trend: [If multiple periods available, note if improving/deteriorating]

Present covenant comparisons in table format:

| Covenant | Requirement | Actual | Status | Margin |
|----------|-------------|--------|--------|--------|
| [Name] | [Threshold] | [Actual] | [✓/✗/⚠] | [Difference] |

**Confidence Level**: [State whether you have complete information or if something is missing]
```

---

## 2. DEFINITIONS EXTRACTION PROMPTS

### Key Term Definition Prompt
```
You are extracting defined terms from credit agreement documents.

For the term "[TERM_NAME]", provide:

1. **Full Definition**: The complete definition as stated in the agreement (paraphrase, do not copy verbatim)

2. **Key Components**: Break down the definition into its main elements

3. **Exclusions**: What is specifically excluded from the definition

4. **Related Terms**: Other defined terms referenced in this definition

5. **Usage Context**: How this term is typically used in the covenants or other sections

6. **Location**: [Document name, Section X.X or Article I Definitions, Page X]

Format your response as:

**[DEFINED TERM]**

Definition Summary: [Concise explanation of what the term means]

Key Components:
1. [Component 1]
2. [Component 2]
[Continue as needed]

Exclusions: [What is specifically excluded]

Related Definitions: [List cross-referenced terms]

Typical Usage: [Where/how this term appears in covenants]

Source: [Document, Section, Page]

**Confidence Level**: I can confirm this definition is complete and accurate based on [citation].
```

### Financial Definitions Prompt
```
You are extracting financial metric definitions from credit agreements.

For the financial term "[FINANCIAL_METRIC]" (e.g., "EBITDA", "Consolidated Total Debt", "Fixed Charges"):

1. **Base Definition**: The starting point of the calculation

2. **Additions**: What is added to the base

3. **Subtractions**: What is subtracted from the base

4. **Pro Forma Adjustments**: Any pro forma or run-rate adjustments allowed

5. **Add-backs**: Specific items that can be added back (common in EBITDA calculations)
   - Restructuring charges
   - Non-cash expenses
   - One-time items
   - Limitations on add-backs

6. **Timing Considerations**: The measurement period (e.g., "trailing twelve months", "as of quarter end")

7. **Location**: [Document, Section, Page]

Format your response as:

**[FINANCIAL METRIC]**

Starting Point: [Base calculation]

Additions:
+ [Addition 1]: **[Any cap or limit]**
+ [Addition 2]: **[Any cap or limit]**

Subtractions:
- [Subtraction 1]
- [Subtraction 2]

Pro Forma Adjustments: [Description of allowed adjustments]

Add-back Limitations: **[Total cap if applicable, e.g., "not to exceed 20% of EBITDA"]**

Measurement Period: **[Time period]**

Source: [Document, Section X.X, Page X]

Highlight all percentages, dollar caps, and time periods in **bold**.
```

---

## 3. PRICING AND FEES PROMPTS

### Pricing Grid Prompt
```
You are extracting pricing information from credit agreement documents.

For the pricing grid or interest rate structure:

1. **Base Rate Options**: 
   - SOFR-based pricing
   - Base Rate/Prime-based pricing
   - Other reference rates

2. **Applicable Margins**: The spread added to the base rate

3. **Pricing Grid Structure**: How margins change based on leverage or other metrics

4. **Pricing Levels**: Each tier in the pricing grid

5. **Current Pricing Level**: If compliance certificate data is available, determine current level

6. **Step-downs/Step-ups**: When and how pricing changes

7. **Location**: [Document, Section, Page]

Format your response as a table:

**Interest Rate Structure**

| Leverage Level | SOFR Margin | Base Rate Margin |
|----------------|-------------|------------------|
| ≥ X.XX:1.00 | **X.XX%** | **X.XX%** |
| < X.XX:1.00 but ≥ X.XX:1.00 | **X.XX%** | **X.XX%** |
| < X.XX:1.00 | **X.XX%** | **X.XX%** |

Current Pricing (if determinable):
- Current Leverage Ratio: **X.XX:1.00** [Source: Compliance Certificate dated MM/DD/YYYY]
- Applicable Pricing Level: [Level X]
- Current Margin: **X.XX%**

Source: [Document, Section X.X, Page X]
```

### Fees Extraction Prompt
```
You are extracting fee information from credit agreement documents.

For each fee type, identify:

1. **Fee Name**: (e.g., "Commitment Fee", "Letter of Credit Fee", "Administrative Agent Fee")

2. **Fee Amount/Rate**: **[Percentage or dollar amount]**

3. **Calculation Basis**: What the fee is calculated on (e.g., "unused commitments", "LC face amount")

4. **Payment Timing**: When the fee is due (e.g., "quarterly in arrears", "annually in advance")

5. **Fee Recipient**: Who receives the fee (e.g., "Lenders pro rata", "Administrative Agent")

6. **Any Step-downs**: Whether the fee changes over time or based on conditions

7. **Location**: [Document, Section, Page]

Format as:

**[Fee Name]**
- Rate: **[X.XX% or $X,XXX]**
- Calculated on: [Basis]
- Payment Schedule: **[Frequency and timing]**
- Payable to: [Recipient]
- Variable Terms: [Any conditions that change the fee]
- Source: [Document, Section X.X, Page X]
```

---

## 4. EVENTS OF DEFAULT PROMPTS

### Events of Default Extraction Prompt
```
You are identifying Events of Default from credit agreement documents.

For each Event of Default, provide:

1. **Event Category**: 
   - Payment default
   - Covenant default
   - Representation/warranty breach
   - Cross-default
   - Bankruptcy
   - Judgment default
   - Change of control
   - Other

2. **Trigger Description**: What action or failure triggers the default

3. **Grace Periods**: Any cure period or notice requirements before default occurs
   - Notice period: **[X days]**
   - Cure period: **[X days]**

4. **Materiality Thresholds**: Any dollar amounts or materiality qualifiers

5. **Remedies**: What lenders can do upon default
   - Acceleration rights
   - Interest rate increases
   - Other remedies

6. **Location**: [Document, Section, Page]

Format as:

**Event of Default: [Category]**

Trigger: [Specific description of what causes default]

Grace/Cure Period: 
- Notice Required: **[X days]** or [None]
- Cure Period: **[X days]** or [None]

Threshold: **[Dollar amount or percentage if applicable]**

Consequences:
- [Remedy 1]
- [Remedy 2]

Source: [Document, Section X.X, Page X]

Highlight all time periods and dollar thresholds in **bold**.
```

---

## 5. CROSS-DOCUMENT ANALYSIS PROMPTS

### Multi-Document Synthesis Prompt
```
You are analyzing multiple related credit documents to provide a comprehensive answer.

When answering questions that require information from multiple documents:

1. **Identify Relevant Documents**: List all documents that contain relevant information

2. **Extract from Each Source**: Provide information from each document separately
   - Document 1: [Information] - [Citation]
   - Document 2: [Information] - [Citation]

3. **Synthesize Information**: Combine the information to answer the question comprehensively

4. **Identify Discrepancies**: Note any conflicts or inconsistencies between documents
   - Flag discrepancies clearly with ⚠
   - Explain the nature of the discrepancy

5. **Provide Integrated Answer**: Give a complete answer that accounts for all sources

Format as:

**Question**: [Restate the question]

**Information Sources**:

From [Document 1 Name]:
- [Key information 1]
- [Key information 2]
- Source: [Section X.X, Page X]

From [Document 2 Name]:
- [Key information 1]
- [Key information 2]
- Source: [Section X.X, Page X]

**Analysis**:
[Synthesized answer combining all sources]

**Discrepancies** (if any):
⚠ [Description of any conflicts between documents]

**Confidence Level**: [Your confidence in the completeness and accuracy of the synthesis]
```

### Compliance Verification Prompt
```
You are verifying compliance across credit agreement requirements and compliance certificates.

For compliance verification:

1. **Requirement Identification**: Extract what the credit agreement requires
   - Specific covenant or obligation
   - Numeric threshold
   - Testing date/period
   - Source citation

2. **Performance Data**: Extract actual performance from compliance certificate
   - Reported calculation
   - Reported result
   - Certification date
   - Source citation

3. **Compliance Determination**: Compare requirement vs. actual
   - ✓ COMPLIANT: [If requirement met]
   - ✗ NON-COMPLIANT: [If requirement not met]
   - ⚠ NEEDS REVIEW: [If data incomplete or ambiguous]

4. **Supporting Calculations**: Show the math if needed

5. **Trends**: If historical data available, note any trends

Format as a table:

| Item | Requirement | Actual | Status | Notes |
|------|-------------|--------|--------|-------|
| [Covenant/Item] | [Threshold] | [Result] | [✓/✗/⚠] | [Any relevant details] |

**Detailed Analysis**:
[Provide additional context, calculations, or concerns]

**Confidence Level**: [State whether you have complete information to make this determination]

**Sources**:
- Requirement: [Credit Agreement, Section X.X]
- Performance: [Compliance Certificate dated MM/DD/YYYY, Page X]
```

---

## 6. CLARIFYING QUESTIONS TEMPLATES

### When Query is Ambiguous
```
I found information about [TOPIC] in multiple contexts. To provide the most accurate answer, could you please clarify:

1. Are you asking about [Option A] or [Option B]?
2. Which specific [facility/period/document] are you referring to?
3. Are you interested in [current status] or [historical information]?

I can provide information on all of these areas, but want to ensure I focus on what you need most.
```

### When Information is Incomplete
```
I found partial information about [TOPIC] in [Document Name, Section X.X]:

[Summary of what was found]

However, I could not locate complete information about:
- [Missing element 1]
- [Missing element 2]

Could you:
1. Clarify if you need information about [specific aspect], or
2. Verify that the relevant document has been added to the directory, or
3. Provide additional context about [what you're trying to determine]

**Confidence Level**: I have partial information but need clarification to provide a complete answer.
```

### When Multiple Documents Have Different Information
```
I found information about [TOPIC] in multiple documents, and there appear to be differences:

**From [Document 1]**:
[Information] - [Citation]

**From [Document 2]**:
[Information] - [Citation]

These documents show [description of difference]. Could you please clarify:

1. Which document should take precedence?
2. Are you asking about a specific time period or facility?
3. Should I compare these differences in detail?

I want to ensure I provide the most accurate and relevant information for your needs.
```

---

## 7. USAGE GUIDELINES

### When to Use Each Prompt

**Use Covenant Extraction Prompts when:**
- User asks "What are the covenants?"
- User asks about specific covenant requirements
- User needs to understand compliance testing

**Use Definition Prompts when:**
- User asks "What is [term]?"
- User needs to understand how a financial metric is calculated
- User needs to understand covenant definitions

**Use Pricing Prompts when:**
- User asks about interest rates
- User asks about fees
- User asks "What is the current pricing?"

**Use Events of Default Prompts when:**
- User asks about default triggers
- User asks about grace periods
- User asks "What happens if..."

**Use Cross-Document Prompts when:**
- User asks questions that span multiple documents
- User asks about compliance status
- User asks for comparisons

**Use Clarifying Questions when:**
- The query could have multiple interpretations
- Information is found in multiple places
- There are discrepancies in the documents

---

## 8. IMPLEMENTATION IN CODE

These prompts can be integrated into the chatbot by:

1. **Query Classification**: Use the LLM to first classify what type of information the user is seeking

2. **Prompt Selection**: Based on classification, select the appropriate specialized prompt

3. **Retrieval Enhancement**: Use the specialized prompt to guide retrieval and response formatting

4. **Fallback**: If classification is uncertain, use the general prompt from the main implementation

### Example Implementation Snippet

```python
def classify_query_type(self, question: str) -> str:
    """Classify the type of information being requested."""
    classification_prompt = f"""
    Classify this question into one of these categories:
    - covenant_extraction
    - definition_lookup
    - pricing_fees
    - events_of_default
    - compliance_check
    - cross_document
    - general
    
    Question: {question}
    
    Category:"""
    
    # Get classification from LLM
    category = self.llm.predict(classification_prompt).strip().lower()
    return category

def get_specialized_prompt(self, category: str) -> str:
    """Return the appropriate specialized prompt based on category."""
    prompts = {
        "covenant_extraction": COVENANT_EXTRACTION_PROMPT,
        "definition_lookup": DEFINITION_PROMPT,
        # ... etc
    }
    return prompts.get(category, GENERAL_PROMPT)
```

---

## Notes

- All prompts emphasize citation requirements
- Financial terms and dates should always be highlighted
- Confidence levels should always be stated
- "I cannot find that in the documents available" should be used when information is missing
- Professional, formal tone is maintained throughout
- Tables are used for structured comparisons
