"""
Restructure generate_pdf.py to use the 5 evaluation criteria as main sections.
This script modifies section titles and TOC to match the NFPC rubric.
"""

with open(r'C:\Users\jaivi\OneDrive\Desktop\upi\generate_pdf.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. Replace the Table of Contents
# ============================================================
old_toc = """toc = [
    '1.  Data Loading & Schema Understanding',
    '2.  Target Variable Deep Analysis',
    '3.  Account-Level EDA (Mule vs Legitimate)',
    '4.  Customer-Level EDA',
    '5.  Transaction-Level EDA',
    '6.  Known Mule Pattern Detection (All 12 Patterns)',
    '7.  Network / Relationship Analysis',
    '8.  Missing Data & Data Quality Observations',
    '9.  Feature Engineering Plan (46 Features)',
    '10. Critical Reasoning & Modelling Strategy',
    '11. Phase 2: Modeling Pipeline & Approach',
    '12. Fraud Domain Analysis & Financial Crime Reasoning',
    '13. Statistical Rigor & Reproducibility',
]
for item in toc:
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, item, new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)"""

new_toc = """# Evaluation Criteria weightage table
pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(20, 60, 120)
pdf.cell(0, 7, 'Report Structure (Aligned with NFPC Evaluation Rubric)', new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(30, 30, 30)
pdf.ln(2)

pdf.add_table(
    ['Section', 'Evaluation Dimension', 'Weight'],
    [['Part 1', 'Exploratory Data Analysis (EDA Quality & Data Understanding)', '25%'],
     ['Part 2', 'Feature Engineering & Innovation', '30%'],
     ['Part 3', 'ML Approach & Analytical Rigor', '25%'],
     ['Part 4', 'Fraud Domain Reasoning', '10%'],
     ['Part 5', 'Clarity of Documentation & Communication', '10%']],
    [20, 130, 20]
)
pdf.ln(3)

toc_items = [
    ('', 'PART 1: EXPLORATORY DATA ANALYSIS (25%)', True),
    ('  ', '1.1  Data Loading & Schema Understanding'),
    ('  ', '1.2  Target Variable Deep Analysis'),
    ('  ', '1.3  Account-Level EDA (Mule vs Legitimate)'),
    ('  ', '1.4  Customer-Level EDA'),
    ('  ', '1.5  Transaction-Level EDA'),
    ('  ', '1.6  Network / Relationship Analysis'),
    ('  ', '1.7  Missing Data & Data Quality'),
    ('  ', '1.8  Hypothesis Tests & Effect Sizes'),
    ('  ', '1.9  EDA Summary Dashboard'),
    ('', '', False),
    ('', 'PART 2: FEATURE ENGINEERING & INNOVATION (30%)', True),
    ('  ', '2.1  Known Mule Pattern Detection (All 12 Patterns)'),
    ('  ', '2.2  Feature Engineering Plan (46 Features)'),
    ('', '', False),
    ('', 'PART 3: ML APPROACH & ANALYTICAL RIGOR (25%)', True),
    ('  ', '3.1  Critical Reasoning & Modelling Strategy'),
    ('  ', '3.2  Phase 2: Modeling Pipeline & Approach'),
    ('', '', False),
    ('', 'PART 4: FRAUD DOMAIN REASONING (10%)', True),
    ('  ', '4.1  Money Laundering Lifecycle & Mule Typology'),
    ('  ', '4.2  Real-World Fraud Scenarios & Flow Analysis'),
    ('  ', '4.3  Regulatory Framework & Compliance'),
    ('  ', '4.4  Investigator Workflow Integration'),
    ('', '', False),
    ('', 'PART 5: DOCUMENTATION & COMMUNICATION (10%)', True),
    ('  ', '5.1  Assumptions & Limitations'),
    ('  ', '5.2  Reproducibility & Environment'),
    ('  ', '5.3  Ethical AI Considerations'),
    ('', '', False),
    ('', 'APPENDICES', True),
    ('  ', 'A.  Interactive Notebook & Colab Link'),
    ('  ', 'B.  Key Code Snippets'),
    ('  ', 'C.  Visualization Index'),
]

for item in toc_items:
    if len(item) == 3 and item[2] == True:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(20, 60, 120)
        pdf.cell(0, 7, item[1], new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(30, 30, 30)
    elif len(item) == 3 and item[2] == False:
        pdf.ln(1)
    else:
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 5.5, item[0] + item[1], new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)"""

content = content.replace(old_toc, new_toc)

# ============================================================
# 2. Rename Section Titles - PART 1: EDA
# ============================================================

# Section 1 -> 1.1
content = content.replace(
    "pdf.section_title('1. Data Loading & Schema Understanding')",
    "# --- PART 1: EXPLORATORY DATA ANALYSIS ---\npdf.add_page()\npdf.set_fill_color(20, 60, 120)\npdf.rect(0, 80, 210, 50, 'F')\npdf.set_y(88)\npdf.set_font('Helvetica', 'B', 28)\npdf.set_text_color(255, 255, 255)\npdf.cell(0, 12, 'PART 1', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', '', 16)\npdf.cell(0, 10, 'Exploratory Data Analysis', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', 'I', 12)\npdf.cell(0, 8, 'EDA Quality & Data Understanding  |  Weight: 25%', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_text_color(30, 30, 30)\n\npdf.add_page()\npdf.section_title('1.1 Data Loading & Schema Understanding')"
)

content = content.replace("pdf.section_title('1.1 Dataset Overview', 3)", "pdf.section_title('1.1.1 Dataset Overview', 3)")
content = content.replace("pdf.section_title('1.2 Entity Relationships', 3)", "pdf.section_title('1.1.2 Entity Relationships', 3)")
content = content.replace("pdf.section_title('1.3 Missing Values Summary', 3)", "pdf.section_title('1.1.3 Missing Values Summary', 3)")

# Section 2 -> 1.2
content = content.replace(
    "pdf.section_title('2. Target Variable Deep Analysis')",
    "pdf.section_title('1.2 Target Variable Deep Analysis')"
)
content = content.replace("pdf.section_title('2.1 Alert Reason Analysis', 3)", "pdf.section_title('1.2.1 Alert Reason Analysis', 3)")
content = content.replace("pdf.section_title('2.2 Temporal Distribution of Mule Flagging', 3)", "pdf.section_title('1.2.2 Temporal Distribution of Mule Flagging', 3)")

# Section 3 -> 1.3
content = content.replace(
    "pdf.section_title('3. Account-Level EDA (Mule vs Legitimate)')",
    "pdf.section_title('1.3 Account-Level EDA (Mule vs Legitimate)')"
)
content = content.replace("pdf.section_title('3.1 Balance Distributions', 3)", "pdf.section_title('1.3.1 Balance Distributions', 3)")
content = content.replace("pdf.section_title('3.2 Product Family Distribution', 3)", "pdf.section_title('1.3.2 Product Family Distribution', 3)")
content = content.replace("pdf.section_title('3.3 Account Status', 3)", "pdf.section_title('1.3.3 Account Status', 3)")
content = content.replace("pdf.section_title('3.4 Account Age Analysis', 3)", "pdf.section_title('1.3.4 Account Age Analysis', 3)")
content = content.replace("pdf.section_title('3.5 KYC & Compliance Flags', 3)", "pdf.section_title('1.3.5 KYC & Compliance Flags', 3)")
content = content.replace("pdf.section_title('3.6 Freeze/Unfreeze Pattern', 3)", "pdf.section_title('1.3.6 Freeze/Unfreeze Pattern', 3)")

# Section 4 -> 1.4
content = content.replace(
    "pdf.section_title('4. Customer-Level EDA')",
    "pdf.section_title('1.4 Customer-Level EDA')"
)
content = content.replace("pdf.section_title('4.1 Demographics', 3)", "pdf.section_title('1.4.1 Demographics', 3)")
content = content.replace("pdf.section_title('4.2 KYC Document Availability', 3)", "pdf.section_title('1.4.2 KYC Document Availability', 3)")
content = content.replace("pdf.section_title('4.3 Digital Banking Adoption', 3)", "pdf.section_title('1.4.3 Digital Banking Adoption', 3)")
content = content.replace("pdf.section_title('4.4 Multi-Account Analysis', 3)", "pdf.section_title('1.4.4 Multi-Account Analysis', 3)")

# Section 5 -> 1.5
content = content.replace(
    "pdf.section_title('5. Transaction-Level EDA')",
    "pdf.section_title('1.5 Transaction-Level EDA')"
)
content = content.replace("pdf.section_title('5.1 Transaction Volume & Amount Distribution', 3)", "pdf.section_title('1.5.1 Transaction Volume & Amount Distribution', 3)")
content = content.replace("pdf.section_title('5.2 Channel Usage Breakdown', 3)", "pdf.section_title('1.5.2 Channel Usage Breakdown', 3)")
content = content.replace("pdf.section_title('5.3 Credit/Debit Analysis', 3)", "pdf.section_title('1.5.3 Credit/Debit Analysis', 3)")
content = content.replace("pdf.section_title('5.4 Temporal Patterns', 3)", "pdf.section_title('1.5.4 Temporal Patterns', 3)")
content = content.replace("pdf.section_title('5.5 Counterparty Diversity', 3)", "pdf.section_title('1.5.5 Counterparty Diversity', 3)")

# Section 7 -> 1.6 (Network analysis moves under EDA)
content = content.replace(
    "pdf.section_title('7. Network / Relationship Analysis')",
    "pdf.section_title('1.6 Network / Relationship Analysis')"
)
content = content.replace("pdf.section_title('7.1 Counterparty Network Metrics', 3)", "pdf.section_title('1.6.1 Counterparty Network Metrics', 3)")
content = content.replace("pdf.section_title('7.2 Shared Counterparties Between Mule Accounts', 3)", "pdf.section_title('1.6.2 Shared Counterparties Between Mule Accounts', 3)")
content = content.replace("pdf.section_title('7.3 Branch-Level Mule Concentration', 3)", "pdf.section_title('1.6.3 Branch-Level Mule Concentration', 3)")

# Section 8 -> 1.7
content = content.replace(
    "pdf.section_title('8. Missing Data & Data Quality Observations')",
    "pdf.section_title('1.7 Missing Data & Data Quality Observations')"
)
content = content.replace("pdf.section_title('8.1 Missingness Correlation with Target', 3)", "pdf.section_title('1.7.1 Missingness Correlation with Target', 3)")
content = content.replace("pdf.section_title('8.2 Label Noise Assessment', 3)", "pdf.section_title('1.7.2 Label Noise Assessment', 3)")
content = content.replace("pdf.section_title('8.3 Data Leakage Concerns', 3)", "pdf.section_title('1.7.3 Data Leakage Concerns', 3)")

# Section 13.1, 13.2 -> 1.8 (Hypothesis tests moves under EDA)
content = content.replace(
    "pdf.section_title('13. Statistical Rigor & Reproducibility')",
    "pdf.section_title('1.8 Statistical Validation of Findings')"
)
content = content.replace("pdf.section_title('13.1 Hypothesis Tests on Key Findings', 3)", "pdf.section_title('1.8.1 Hypothesis Tests on Key Findings', 3)")
content = content.replace("pdf.section_title('13.2 Effect Size Analysis', 3)", "pdf.section_title('1.8.2 Effect Size Analysis', 3)")

# Section 13.5 -> 1.9 (Summary dashboard stays under EDA)
content = content.replace("pdf.section_title('13.5 EDA Summary Dashboard', 3)", "pdf.section_title('1.9 EDA Summary Dashboard')")

# ============================================================
# 3. Rename Section Titles - PART 2: FEATURE ENGINEERING
# ============================================================

# Section 6 -> Part 2 header + 2.1
content = content.replace(
    "pdf.section_title('6. Known Mule Pattern Detection')",
    "# --- PART 2: FEATURE ENGINEERING & INNOVATION ---\npdf.add_page()\npdf.set_fill_color(34, 139, 34)\npdf.rect(0, 80, 210, 50, 'F')\npdf.set_y(88)\npdf.set_font('Helvetica', 'B', 28)\npdf.set_text_color(255, 255, 255)\npdf.cell(0, 12, 'PART 2', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', '', 16)\npdf.cell(0, 10, 'Feature Engineering & Innovation', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', 'I', 12)\npdf.cell(0, 8, 'Creativity and Relevance of Features  |  Weight: 30%', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_text_color(30, 30, 30)\n\npdf.add_page()\npdf.section_title('2.1 Known Mule Pattern Detection')"
)

content = content.replace("pdf.section_title('6.1 Dormant Activation', 3)", "pdf.section_title('2.1.1 Dormant Activation', 3)")
content = content.replace("pdf.section_title('6.2 Structuring (Near-Threshold Amounts)', 3)", "pdf.section_title('2.1.2 Structuring (Near-Threshold Amounts)', 3)")
content = content.replace("pdf.section_title('6.3 Rapid Pass-Through', 3)", "pdf.section_title('2.1.3 Rapid Pass-Through', 3)")
content = content.replace("pdf.section_title('6.4 Fan-In / Fan-Out', 3)", "pdf.section_title('2.1.4 Fan-In / Fan-Out', 3)")
content = content.replace("pdf.section_title('6.5 Geographic Anomaly', 3)", "pdf.section_title('2.1.5 Geographic Anomaly', 3)")
content = content.replace("pdf.section_title('6.6 New Account High Value', 3)", "pdf.section_title('2.1.6 New Account High Value', 3)")
content = content.replace("pdf.section_title('6.7 Income Mismatch', 3)", "pdf.section_title('2.1.7 Income Mismatch', 3)")
content = content.replace("pdf.section_title('6.8 Post-Mobile-Change Spike', 3)", "pdf.section_title('2.1.8 Post-Mobile-Change Spike', 3)")
content = content.replace("pdf.section_title('6.9 Round Amount Patterns', 3)", "pdf.section_title('2.1.9 Round Amount Patterns', 3)")
content = content.replace("pdf.section_title('6.10 Layered/Subtle Patterns', 3)", "pdf.section_title('2.1.10 Layered/Subtle Patterns', 3)")
content = content.replace("pdf.section_title('6.11 Salary Cycle Exploitation', 3)", "pdf.section_title('2.1.11 Salary Cycle Exploitation', 3)")
content = content.replace("pdf.section_title('6.12 Branch-Level Collusion', 3)", "pdf.section_title('2.1.12 Branch-Level Collusion', 3)")

# Section 9 -> 2.2
content = content.replace(
    "pdf.section_title('9. Feature Engineering Plan')",
    "pdf.section_title('2.2 Feature Engineering Plan (46 Features)')"
)

# ============================================================
# 4. Rename Section Titles - PART 3: ML APPROACH
# ============================================================

# Section 10 -> Part 3 header + 3.1
content = content.replace(
    "pdf.section_title('10. Critical Reasoning & Modelling Strategy')",
    "# --- PART 3: ML APPROACH & ANALYTICAL RIGOR ---\npdf.add_page()\npdf.set_fill_color(180, 60, 30)\npdf.rect(0, 80, 210, 50, 'F')\npdf.set_y(88)\npdf.set_font('Helvetica', 'B', 28)\npdf.set_text_color(255, 255, 255)\npdf.cell(0, 12, 'PART 3', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', '', 16)\npdf.cell(0, 10, 'ML Approach & Analytical Rigor', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', 'I', 12)\npdf.cell(0, 8, 'Soundness of Modeling Approach  |  Weight: 25%', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_text_color(30, 30, 30)\n\npdf.add_page()\npdf.section_title('3.1 Critical Reasoning & Modelling Strategy')"
)

content = content.replace("pdf.section_title('10.1 Key Findings Summary', 3)", "pdf.section_title('3.1.1 Key Findings Summary', 3)")
content = content.replace("pdf.section_title('10.2 Modelling Strategy for Phase 2', 3)", "pdf.section_title('3.1.2 Modelling Strategy for Phase 2', 3)")
content = content.replace("pdf.section_title('10.3 Limitations & Caveats', 3)", "pdf.section_title('3.1.3 Limitations & Caveats', 3)")
content = content.replace("pdf.section_title('10.4 Ethical AI Considerations', 3)", "pdf.section_title('3.1.4 Ethical AI Considerations', 3)")

# Section 11 -> 3.2
content = content.replace(
    "pdf.section_title('11. Phase 2: Modeling Pipeline & Approach')",
    "pdf.section_title('3.2 Phase 2: Modeling Pipeline & Approach')"
)

content = content.replace("pdf.section_title('11.1 Key EDA Conclusions Driving Model Design', 3)", "pdf.section_title('3.2.1 Key EDA Conclusions Driving Model Design', 3)")
content = content.replace("pdf.section_title('11.2 End-to-End Pipeline Architecture', 3)", "pdf.section_title('3.2.2 End-to-End Pipeline Architecture', 3)")
content = content.replace("pdf.section_title('11.3 Supervised Learning Approach', 3)", "pdf.section_title('3.2.3 Supervised Learning Approach', 3)")
content = content.replace("pdf.section_title('11.4 Unsupervised Anomaly Detection', 3)", "pdf.section_title('3.2.4 Unsupervised Anomaly Detection', 3)")
content = content.replace("pdf.section_title('11.5 Graph-Based Learning', 3)", "pdf.section_title('3.2.5 Graph-Based Learning', 3)")
content = content.replace("pdf.section_title('11.6 Ensemble Strategy', 3)", "pdf.section_title('3.2.6 Ensemble Strategy', 3)")
content = content.replace("pdf.section_title('11.7 Evaluation Framework', 3)", "pdf.section_title('3.2.7 Evaluation Framework', 3)")
content = content.replace("pdf.section_title('11.8 Model Explainability (SHAP Analysis)', 3)", "pdf.section_title('3.2.8 Model Explainability (SHAP Analysis)', 3)")
content = content.replace("pdf.section_title('11.9 Production Deployment Considerations', 3)", "pdf.section_title('3.2.9 Production Deployment Considerations', 3)")
content = content.replace("pdf.section_title('11.10 Implementation Timeline', 3)", "pdf.section_title('3.2.10 Implementation Timeline', 3)")

# ============================================================
# 5. Rename Section Titles - PART 4: FRAUD DOMAIN REASONING
# ============================================================

content = content.replace(
    "pdf.section_title('12. Fraud Domain Analysis & Financial Crime Reasoning')",
    "# --- PART 4: FRAUD DOMAIN REASONING ---\npdf.add_page()\npdf.set_fill_color(128, 0, 128)\npdf.rect(0, 80, 210, 50, 'F')\npdf.set_y(88)\npdf.set_font('Helvetica', 'B', 28)\npdf.set_text_color(255, 255, 255)\npdf.cell(0, 12, 'PART 4', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', '', 16)\npdf.cell(0, 10, 'Fraud Domain Reasoning', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', 'I', 12)\npdf.cell(0, 8, 'Mapping ML to Real-World Fraud  |  Weight: 10%', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_text_color(30, 30, 30)\n\npdf.add_page()\npdf.section_title('4. Fraud Domain Analysis & Financial Crime Reasoning')"
)

content = content.replace("pdf.section_title('12.1 Money Laundering Lifecycle & Mule Role', 3)", "pdf.section_title('4.1 Money Laundering Lifecycle & Mule Role', 3)")
content = content.replace("pdf.section_title('12.2 Mule Account Typology', 3)", "pdf.section_title('4.2 Mule Account Typology', 3)")
content = content.replace("pdf.section_title('12.3 Real-World Fraud Scenarios from Data', 3)", "pdf.section_title('4.3 Real-World Fraud Scenarios from Data', 3)")
content = content.replace("pdf.section_title('12.4 Regulatory Framework & Compliance Context', 3)", "pdf.section_title('4.4 Regulatory Framework & Compliance Context', 3)")
content = content.replace("pdf.section_title('12.5 Investigator Workflow Integration', 3)", "pdf.section_title('4.5 Investigator Workflow Integration', 3)")

# ============================================================
# 6. Rename Section Titles - PART 5: DOCUMENTATION
# ============================================================

# Section 13.3  -> 5.1
content = content.replace(
    "pdf.section_title('13.3 Assumptions & Limitations Disclosure', 3)",
    "# --- PART 5: DOCUMENTATION & COMMUNICATION ---\npdf.add_page()\npdf.set_fill_color(50, 50, 50)\npdf.rect(0, 80, 210, 50, 'F')\npdf.set_y(88)\npdf.set_font('Helvetica', 'B', 28)\npdf.set_text_color(255, 255, 255)\npdf.cell(0, 12, 'PART 5', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', '', 16)\npdf.cell(0, 10, 'Documentation & Communication', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_font('Helvetica', 'I', 12)\npdf.cell(0, 8, 'Clarity, Reproducibility & Ethics  |  Weight: 10%', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")\npdf.set_text_color(30, 30, 30)\n\npdf.add_page()\npdf.section_title('5. Documentation & Communication')\npdf.body_text('This section addresses the clarity, reproducibility, and ethical considerations '\n              'of the analysis, ensuring that results can be independently verified and '\n              'responsibly deployed.')\n\npdf.section_title('5.1 Assumptions & Limitations Disclosure', 3)"
)

content = content.replace("pdf.section_title('13.4 Reproducibility Checklist', 3)", "pdf.section_title('5.2 Reproducibility Checklist', 3)")

# Also update the comment block headers
content = content.replace("# SECTION 12: FRAUD DOMAIN ANALYSIS", "# PART 4: FRAUD DOMAIN REASONING")
content = content.replace("# SECTION 13: STATISTICAL RIGOR & REPRODUCIBILITY", "# PART 1 (cont): STATISTICAL VALIDATION")

# ============================================================
# 7. Update cover page subtitle if present
# ============================================================
content = content.replace(
    "pdf.cell(0, 10, 'Comprehensive Exploratory Data Analysis', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")",
    "pdf.cell(0, 10, 'Comprehensive EDA, Feature Engineering & Modeling Pipeline', align='C', new_x=\"LMARGIN\", new_y=\"NEXT\")"
)

# ============================================================
# 8. Clean non-ASCII
# ============================================================
import re
content = re.sub(r'[^\x00-\x7f]', '=', content)

# ============================================================
# 9. Write back
# ============================================================
with open(r'C:\Users\jaivi\OneDrive\Desktop\upi\generate_pdf.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Restructuring complete!")
print("Sections renumbered to 5-Part structure matching evaluation rubric.")
