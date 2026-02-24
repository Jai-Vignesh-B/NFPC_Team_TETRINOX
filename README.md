<p align="center">
  <img src="https://img.shields.io/badge/NFPC-Phase%201-blueviolet?style=for-the-badge" alt="NFPC Phase 1"/>
  <img src="https://img.shields.io/badge/Team-TETRINOX-orange?style=for-the-badge" alt="Team TETRINOX"/>
  <img src="https://img.shields.io/badge/RBIH%20x%20IIT%20Delhi-TRYST-red?style=for-the-badge" alt="RBIH x IIT Delhi"/>
</p>

<h1 align="center">🛡️ Mule Account Detection — NFPC Phase 1</h1>
<h3 align="center">National Fraud Prevention Challenge | Reserve Bank Innovation Hub × IIT Delhi TRYST</h3>

<p align="center">
  <em>Comprehensive Exploratory Data Analysis, Feature Engineering & Modeling Strategy for detecting mule accounts used in financial fraud</em>
</p>

---

## 📋 Table of Contents

- [About the Challenge](#-about-the-challenge)
- [Team TETRINOX](#-team-tetrinox)
- [Dataset Overview](#-dataset-overview)
- [Entity Relationships](#-entity-relationships)
- [EDA — Key Findings](#-eda--key-findings)
  - [Target Variable Analysis](#1-target-variable-analysis)
  - [Account-Level Analysis](#2-account-level-analysis)
  - [Customer-Level Analysis](#3-customer-level-analysis)
  - [Transaction-Level Analysis](#4-transaction-level-analysis)
- [Mule Pattern Detection (12 Patterns)](#-mule-pattern-detection-12-patterns)
- [Network & Relationship Analysis](#-network--relationship-analysis)
- [Data Quality & Leakage Assessment](#-data-quality--leakage-assessment)
- [Feature Engineering Plan (46 Features)](#-feature-engineering-plan-46-features)
- [Phase 2 — Modeling Pipeline](#-phase-2--modeling-pipeline)
- [Fraud Domain Reasoning](#-fraud-domain-reasoning)
- [Statistical Rigor & Reproducibility](#-statistical-rigor--reproducibility)
- [Repository Structure](#-repository-structure)
- [How to Reproduce](#-how-to-reproduce)

---

## 🏦 About the Challenge

The **National Fraud Prevention Challenge (NFPC)** is a multi-stage AI hackathon launched by the **Reserve Bank Innovation Hub (RBIH)** along with **IIT Delhi TRYST** to detect **mule accounts** used in financial fraud — directly contributing to RBIH's [MuleHunter.ai™](https://www.rbihub.in/) platform.

**Phase 1 Objectives:**
- Perform thorough Exploratory Data Analysis (EDA) on labelled synthetic datasets
- Design innovative supervised & unsupervised features capturing mule-like behavior
- Demonstrate analytical reasoning connecting data insights to real-world financial crime patterns

---

## 👥 Team TETRINOX

> Team submission for the National Fraud Prevention Challenge (NFPC)

---

## 📊 Dataset Overview

The dataset comprises **7 interlinked tables** spanning ~40K customers, ~40K accounts, and **7.4 million transactions**:

| Table | Rows | Columns | Description |
|---|---|---|---|
| `customers.csv` | 39,988 | 14 | Customer demographics, KYC flags, digital banking flags |
| `accounts.csv` | 40,038 | 22 | Account status, balances, branch info, compliance flags |
| `transactions` | 7,424,845 | 8 | Transaction records (6 CSV parts, ~550 MB total) |
| `customer_account_linkage.csv` | 40,038 | 2 | Maps customers to accounts |
| `product_details.csv` | 39,988 | 11 | Loan, credit card, OD, savings holdings |
| `train_labels.csv` | 24,023 | 5 | Mule labels + alert metadata |
| `test_accounts.csv` | 16,015 | 1 | Test set account IDs |

### Missing Values Summary

| Table | Column | Missing % | Significance |
|---|---|---|---|
| `customers` | `aadhaar_available` | 24.3% | Mules have 9.1pp more Aadhaar missing |
| `accounts` | `last_mobile_update_date` | 84.9% | Only 15% have updated mobile |
| `accounts` | `freeze_date` | 96.7% | Mostly populated for mule accounts |
| `accounts` | `unfreeze_date` | 98.9% | Strongly correlated with mule flag |
| `products` | `loan_sum` | 78.7% | Most customers have no loans |
| `train_labels` | `mule_flag_date` | 98.9% | Only populated for confirmed mules |

---

## 🔗 Entity Relationships

```
customers ──(customer_id)──> linkage ──(account_id)──> accounts
                                                           │
                                                      (account_id)
                                                           │
                                                           v
                                                      transactions

customers ──(customer_id)──> product_details
accounts  ──(account_id)──> train_labels / test_accounts
```

---

## 🔍 EDA — Key Findings

### 1. Target Variable Analysis

**Class Distribution:** 23,760 legitimate (98.9%) vs **263 mule (1.09%)**

> ⚠️ **Critical:** Extreme class imbalance with ~90:1 ratio. Requires SMOTE, class weights, and focal loss during modeling.

<p align="center">
  <img src="plots/target_distribution.png" width="600" alt="Target Distribution"/>
</p>

**Alert Reasons for Mule Accounts:**

| Alert Reason | Count | % of Mules |
|---|---|---|
| Routine Investigation | 55 | 20.9% |
| Rapid Movement of Funds | 22 | 8.4% |
| Structuring Transactions Below Threshold | 18 | 6.8% |
| Branch Cluster Investigation | 17 | 6.5% |
| Dormant Account Reactivation | 17 | 6.5% |
| Income-Transaction Mismatch | 17 | 6.5% |
| Unusual Fund Flow Pattern | 17 | 6.5% |
| High-Value Activity on New Account | 16 | 6.1% |

**Branch Flagging:** 162 branches flagged mules; top 5 branches account for **39.2%** of all mule flags.

---

### 2. Account-Level Analysis

#### Balance Distributions (Mule vs Legitimate)

<p align="center">
  <img src="plots/balance_distributions.png" width="700" alt="Balance Distributions"/>
</p>

| Metric | Legitimate (Mean) | Mule (Mean) | Legitimate (Median) | Mule (Median) |
|---|---|---|---|---|
| `avg_balance` | ₹53,282 | **₹-26,562** | ₹5,260 | ₹3,561 |
| `monthly_avg_balance` | ₹52,861 | ₹-20,981 | ₹5,214 | ₹3,394 |
| `quarterly_avg_balance` | ₹51,438 | ₹-23,227 | ₹5,130 | ₹3,391 |

#### Account Status — Strongest Signal

| Status | Legitimate | Mule | Legit % | Mule % |
|---|---|---|---|---|
| Active | 23,275 | 158 | 98.0% | 60.1% |
| **Frozen** | 485 | **105** | 2.0% | **39.9%** |

> 🔴 **39.9%** of mule accounts are frozen vs only **2.0%** of legitimate accounts (+56pp difference). However, freeze may be a *consequence* of detection — **potential data leakage**.

#### Other Account-Level Signals

- **Account Age:** Legit median 805 days | Mule 751 days (newer accounts slightly more likely to be mules)
- **Rural Branches:** Legit 11.7% | Mule 16.0% (+4.3pp)
- **Cheque Availed:** Legit 36.2% | Mule 39.9% (+3.7pp)

<p align="center">
  <img src="plots/account_age_distribution.png" width="600" alt="Account Age"/>
</p>

---

### 3. Customer-Level Analysis

<p align="center">
  <img src="plots/customer_demographics.png" width="700" alt="Demographics"/>
</p>

- **Age & Tenure:** No significant difference (Legit ~49.5 yrs, Mule ~49.8 yrs)
- **Aadhaar Availability:** Legit 47.1% | Mule **38.0%** (-9.1pp — missing Aadhaar may indicate incomplete KYC)
- **Multi-Account Holders:** Legit **0.2%** | Mule **3.8%** — mules are **19x more likely** to hold multiple accounts

<p align="center">
  <img src="plots/digital_banking_adoption.png" width="600" alt="Digital Banking"/>
</p>

---

### 4. Transaction-Level Analysis

<p align="center">
  <img src="plots/txn_volume_distribution.png" width="700" alt="Transaction Volume"/>
</p>

| Metric | Legitimate (Median) | Mule (Median) | **Ratio** |
|---|---|---|---|
| Transaction Count | 38.0 | 67.5 | **1.78x** |
| Total Volume | ₹314,056 | ₹1,984,011 | **6.32x** |
| Avg Amount | ₹7,424 | ₹14,852 | **2.00x** |
| Unique Counterparties | 10 | 30.5 | **3.05x** |

> 💡 Mule accounts process **6.3x** more total volume and interact with **3x** more counterparties.

<p align="center">
  <img src="plots/channel_usage.png" width="600" alt="Channel Usage"/>
  <br/>
  <img src="plots/temporal_patterns.png" width="600" alt="Temporal Patterns"/>
  <br/>
  <img src="plots/counterparty_diversity.png" width="600" alt="Counterparty Diversity"/>
</p>

---

## 🕵️ Mule Pattern Detection (12 Patterns)

All **12 known mule behavior patterns** from the dataset documentation were systematically investigated:

| # | Pattern | Key Finding | Signal Strength |
|---|---|---|---|
| 1 | **Dormant Activation** | Max dormancy gap: Legit 86d vs Mule 81d | Moderate |
| 2 | **Structuring** | Near-₹50K txns: Legit 0.72% vs Mule **2.61% (3.6x)** | 🔴 **Strong** |
| 3 | **Rapid Pass-Through** | 24h credit-debit match: **44.9%** of mule accounts | 🔴 **Strong** |
| 4 | **Fan-In / Fan-Out** | Credit sources: Legit 8 vs Mule **20 (2.5x)** | 🔴 **Strong** |
| 5 | **Geographic Anomaly** | PIN mismatch: Legit 33.8% vs Mule 38.8% (+5pp) | Moderate |
| 6 | **New Account High Value** | New acct volume: Legit ₹310K vs Mule **₹1.06M (3.4x)** | 🔴 **Strong** |
| 7 | **Income Mismatch** | Volume/Balance: Legit 34.4 vs Mule **247.6 (7.2x)** | 🔴 **Very Strong** |
| 8 | **Post-Mobile-Change Spike** | Mobile update rate: Legit 14.7% vs Mule 20.5% | Moderate |
| 9 | **Round Amount Patterns** | Round amounts: Legit 8.79% vs Mule 8.95% | ❌ Weak |
| 10 | **Layered/Subtle** | Combined weak signals | Composite |
| 11 | **Salary Cycle Exploitation** | Month-boundary ratio: Legit 18.9% vs Mule 19.5% | ❌ Weak |
| 12 | **Branch-Level Collusion** | 250 branches >95th percentile; some at **100% mule rate** | 🔴 **Strong** |

<p align="center">
  <img src="plots/structuring_pattern.png" width="600" alt="Structuring Pattern"/>
  <br/>
  <img src="plots/branch_mule_concentration.png" width="600" alt="Branch Mule Concentration"/>
</p>

---

## 🌐 Network & Relationship Analysis

| Metric | Legitimate (Median) | Mule (Median) |
|---|---|---|
| In-Degree (credit counterparties) | 8 | **20** |
| Out-Degree (debit counterparties) | 8 | **21** |
| Total Degree | 10 | **30** |

- **421 counterparties** shared by 2+ mule accounts (guilt-by-association signal)
- **6 counterparties** shared by 5+ mule accounts (network hubs)
- Max mule accounts sharing one counterparty: **6**

<p align="center">
  <img src="plots/branch_analysis.png" width="700" alt="Branch Analysis"/>
</p>

---

## ⚠️ Data Quality & Leakage Assessment

### Data Leakage Warnings

> 🚨 **CRITICAL:** The following columns must NOT be used as features:

| Column | Risk Level | Reason |
|---|---|---|
| `mule_flag_date` | 🔴 **HIGH** | Only populated for flagged mules |
| `alert_reason` | 🔴 **HIGH** | Direct indicator of mule status |
| `flagged_by_branch` | 🔴 **HIGH** | Post-flag data only |
| `account_status` (frozen) | 🟡 **MEDIUM** | May be a consequence of mule detection |
| `freeze_date` | 🟡 **MEDIUM** | Freeze may result from flagging |

**Mitigation:** Use only features available *before* the account is flagged. Temporal features computed up to a censoring date.

### Label Noise

> The dataset README states: *"Labels may contain noise. Not all labels are guaranteed to be correct."*

**Implications:** Models must incorporate label smoothing, noise-robust losses (symmetric cross-entropy), and confident learning (cleanlab).

---

## 🧬 Feature Engineering Plan (46 Features)

**46 engineered features** organized into 5 categories, each backed by EDA evidence:

### Category A: Behavioral Transaction Features (15)

| # | Feature | Computation | EDA Justification |
|---|---|---|---|
| 1 | `txn_count` | Count per account | 1.78x ratio (Sec 5.1) |
| 2 | `total_volume` | Sum(\|amount\|) | 6.32x ratio (Sec 5.1) |
| 3 | `avg_txn_amount` | Mean(\|amount\|) | 2x ratio |
| 4 | `median_txn_amount` | Median(\|amount\|) | Robust central tendency |
| 5 | `max_single_txn` | Max(\|amount\|) | Large single txns in mules |
| 6 | `txn_amount_std` | Std(amount) | High variability = structuring |
| 7 | `txn_amount_skewness` | Skew(amount) | Asymmetric patterns |
| 8 | `credit_debit_ratio` | Credit / (Debit+1) | Pass-through signal (Sec 5.3) |
| 9 | `unique_channels` | Nunique(channel) | Channel diversity (Sec 5.2) |
| 10 | `dominant_channel_pct` | Max_ch / total | Channel concentration |
| 11 | `unique_counterparties` | Nunique(cp) | 3.05x ratio (Sec 5.5) |
| 12 | `counterparty_entropy` | Shannon entropy | Spread vs concentration |
| 13 | `reversal_count` | Count(amount<0) | Disputed/suspicious activity |
| 14 | `reversal_rate` | Reversals / total | Normalized frequency |
| 15 | `near_threshold_fraction` | ₹45K-50K / total | 3.6x structuring signal (Sec 6.2) |

### Category B: Temporal Features (10)

| # | Feature | Computation | EDA Justification |
|---|---|---|---|
| 16 | `night_txn_ratio` | 10PM-6AM / total | Temporal pattern (Sec 5.4) |
| 17 | `weekend_txn_ratio` | Weekend / total | Weekend behavior |
| 18 | `txn_velocity_7d` | Max 7-day window | Burst detection (Sec 6.1) |
| 19 | `txn_velocity_30d` | Max 30-day window | Monthly burst |
| 20 | `velocity_ratio_7d_30d` | 7d / 30d velocity | Activity concentration |
| 21 | `max_daily_txn_count` | Highest daily txns | Extreme daily activity |
| 22 | `max_daily_txn_volume` | Highest daily volume | Extreme daily volume |
| 23 | `burst_score` | Max/mean daily vol | Spikiness of activity |
| 24 | `dormancy_days_before_burst` | Max gap → burst | Dormant activation (Sec 6.1) |
| 25 | `post_mobile_change_velocity` | After/before ratio | Post-mobile-change spike (Sec 6.8) |

### Category C: Graph/Network Features (8)

| # | Feature | Computation | EDA Justification |
|---|---|---|---|
| 26 | `in_degree` | Unique credit CPs | 2.5x ratio (Sec 7.1) |
| 27 | `out_degree` | Unique debit CPs | 2.6x ratio |
| 28 | `fan_in_out_ratio` | In / (Out+1) | Fan-in/fan-out asymmetry (Sec 6.4) |
| 29 | `shared_mule_counterparties` | CPs in common with mules | 421 shared CPs (Sec 7.2) |
| 30 | `mule_overlap_rate` | Shared / total CPs | Normalized network overlap |
| 31 | `branch_mule_concentration` | Branch mule rate | Branch collusion (Sec 6.12) |
| 32 | `branch_mule_rank` | Percentile rank | Relative branch risk |
| 33 | `degree_centrality` | Degree / max(degree) | Network importance |

### Category D: Account/Customer Profile Features (8)

| # | Feature | Computation | EDA Justification |
|---|---|---|---|
| 34 | `account_age_days` | Ref - opening date | New accounts riskier (Sec 6.6) |
| 35 | `relationship_tenure_days` | Ref - relationship start | Customer maturity |
| 36 | `kyc_document_count` | PAN + Aadhaar + Passport | KYC completeness (Sec 4.2) |
| 37 | `digital_channel_count` | Sum of digital flags | Digital engagement (Sec 4.3) |
| 38 | `balance_volatility` | Std(monthly, quarterly, daily) | Balance stability |
| 39 | `pin_mismatch` | Customer PIN ≠ Branch PIN | Geographic anomaly (Sec 6.5) |
| 40 | `product_holding_diversity` | Non-zero product types | Diversification metric |
| 41 | `total_liability_ratio` | (Loan+CC+OD) / SA | Leverage indicator |

### Category E: Anomaly/Composite Features (5)

| # | Feature | Computation | EDA Justification |
|---|---|---|---|
| 42 | `pass_through_score` | Credit-debit 24h match rate | 44.9% of mules (Sec 6.3) |
| 43 | `structuring_score` | Weighted near-threshold count | 3.6x signal (Sec 6.2) |
| 44 | `round_amount_fraction` | Round txns / total | Synthetic payment pattern (Sec 6.9) |
| 45 | `salary_cycle_exploitation` | Month-boundary volume ratio | Salary abuse (Sec 6.11) |
| 46 | `layered_composite_score` | Weighted sum of weak signals | Subtle multi-pattern (Sec 6.10) |

---

## 🤖 Phase 2 — Modeling Pipeline

### End-to-End Architecture

```
  Raw Data (7 CSVs)  →  Feature Engineering  →  Feature Store (46 features/account)
  7.4M transactions       46 features/acct        features.csv
                                                       │
                   ┌───────────────────────────────────┤
                   │                │                   │
            ┌──────▼──────┐  ┌─────▼───────┐  ┌───────▼────────┐
            │ Supervised  │  │ Unsupervised │  │  Graph-Based   │
            │ LightGBM    │  │ Isolation For│  │  Node2Vec/GNN  │
            │ XGBoost     │  │ Autoencoder  │  │  GraphSAGE     │
            └──────┬──────┘  └─────┬───────┘  └───────┬────────┘
                   │                │                   │
                   └───────────────┬───────────────────┘
                                   │
                          ┌────────▼────────┐
                          │ Ensemble Layer  │
                          │ Weighted Average│
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │ Final Prediction│
                          │ + SHAP Explain  │
                          └─────────────────┘
```

### Supervised Learning

**Primary: LightGBM** — chosen for tabular data superiority, native categorical support, built-in imbalance handling.

| Hyperparameter | Value | Rationale |
|---|---|---|
| `objective` | `binary` | Binary mule vs legitimate |
| `metric` | `average_precision` | AUC-PR preferred for imbalanced data |
| `scale_pos_weight` | ~90 | Compensate 90:1 class imbalance |
| `num_leaves` | 63-127 | Deeper trees for complex interactions |
| `learning_rate` | 0.01-0.05 | Low rate + early stopping |

**Imbalance Handling (Multi-Pronged):**
- SMOTE + Tomek Links — synthetic oversampling + boundary cleaning
- Focal Loss — focus on hard boundary cases
- Class Weights — 90x positive class weight
- Threshold Tuning — optimize on validation F1-score
- Cost-Sensitive Learning — higher mule misclassification cost

### Unsupervised Anomaly Detection

| Model | Approach | Output |
|---|---|---|
| Isolation Forest | Tree-based anomaly isolation | Anomaly score per account |
| Autoencoder | Learn normal → flag deviations | Reconstruction error |
| HDBSCAN | Density-based clustering | Cluster labels + outlier flag |
| Local Outlier Factor | K-NN density comparison | LOF score |

### Graph-Based Learning

| Method | Approach | Output |
|---|---|---|
| Node2Vec | Random walks → Word2Vec embeddings | 64-dim embedding |
| GraphSAGE | Neighborhood aggregation via NN | Learned representations |
| GCN | Message passing between nodes | Guilt-by-association scores |
| PageRank | Importance propagation | Centrality score |

### Ensemble Strategy

```
P(mule) = 0.40×LightGBM + 0.20×XGBoost + 0.10×IsoForest
         + 0.10×Autoencoder + 0.15×GNN + 0.05×MetaLearner
```

Weights optimized via Bayesian optimization maximizing AUC-PR.

### Evaluation Framework

| Metric | Target | Why |
|---|---|---|
| **AUC-PR** | > 0.60 | Primary — robust to imbalance |
| F1-Score | > 0.50 | Precision-recall balance |
| Precision@10% | > 0.40 | Investigation efficiency |
| Recall@5%FPR | > 0.70 | Detection at low false-positive |
| AUC-ROC | > 0.90 | Baseline comparison |

---

## 🔐 Fraud Domain Reasoning

### Money Laundering Lifecycle & Mule Role

```
PREDICATE OFFENSE      →    PLACEMENT           →    LAYERING              →    INTEGRATION
(Source of funds)            (Entry into system)      (Obscure trail)            (Clean funds)

Fraud / Scam /              Victim transfers          Mule Account              Cash withdrawal
Cybercrime /         →      funds to mule      →      splits, layers,    →      Investment
Drug trafficking            account directly          passes through            Crypto purchase

                            Pattern 6.6:              Patterns 6.2-6.4:        Pattern 6.7:
                            New Acct High Value       Structuring (3.6x)        Income Mismatch
                            (3.4x volume)             Pass-Through (44.9%)      (7.2x ratio)
                                                      Fan-In/Out (2.5x)
```

### Mule Account Typology

| Mule Type | Description | EDA Evidence | Detection Strategy |
|---|---|---|---|
| **Professional Mule** | Accounts opened for laundering | New accts with 3.4x volume | New-account-high-value features |
| **Recruited Mule** | Existing accounts recruited | Dormant reactivation | Velocity spike after dormancy |
| **Unwitting Mule** | Holders unaware of criminal use | Pass-through without structuring | Anomalous inflow-outflow timing |
| **Account Takeover** | Legitimate accounts compromised | Post-mobile-change +5.8pp | Behavior change after contact update |
| **Syndicate Mule** | Organized mule network | 421 shared counterparties | Graph community detection |
| **Branch-Facilitated** | Insider collusion | 100% mule rate branches | Branch concentration features |

### Real-World Fraud Scenarios

**Scenario A — The Structuring Mule:**
```
Day 1: Account receives ₹49,500 from Source A   (just below ₹50K threshold)
Day 1: Account receives ₹48,900 from Source B   (again below threshold)
Day 2: Account receives ₹49,800 from Source C   (structured deposit)
Day 2: Account transfers ₹1,47,000 to Account X (aggregation + layering)

→ Mule accounts show 3.6x higher near-threshold transaction rate
```

**Scenario B — The Pass-Through Mule:**
```
10:00 AM: Credit of ₹2,00,000 from Account Y
10:45 AM: Debit of ₹1,95,000 to Account Z     (within 1 hour, ~2.5% fee)
Balance before: ₹5,200 | Balance after: ₹10,200

→ 44.9% of mule accounts exhibit this exact pattern
```

**Scenario C — The Syndicate Network:**
```
Mule M1 ──→ Counterparty CP_007 ←── Mule M2
Mule M3 ──→ Counterparty CP_007 ←── Mule M4
Mule M5 ──→ Counterparty CP_007

→ 421 counterparties shared by 2+ mule accounts
→ Max: 6 mule accounts converging on a single counterparty
```

### Regulatory Alignment

| Regulation | Requirement | Our Coverage |
|---|---|---|
| PMLA 2002 | Suspicious Transaction Reporting | ₹50K threshold analysis |
| RBI KYC Master Dir. | Customer Due Diligence | KYC completeness analysis |
| FATF Recommendations | Risk-Based Approach to AML | 46-feature risk scoring |
| IT Act 2000 Sec 43A | Data protection in fraud systems | No PII in features |

---

## 📐 Statistical Rigor & Reproducibility

### Key Findings Summary

| # | Finding | Signal | Impact |
|---|---|---|---|
| 1 | Volume/Balance ratio 7.2x | 🔴 Very Strong | Top feature for gradient boosting |
| 2 | Structuring near ₹50K (3.6x) | 🔴 Strong | Threshold-based feature |
| 3 | Pass-through 24h (44.9%) | 🔴 Strong | Temporal sequence feature |
| 4 | Multi-account (19x) | 🔴 Strong | Graph connectivity feature |
| 5 | Shared counterparties (421) | 🟡 Medium | Guilt-by-association via GNN |
| 6 | Frozen accounts (39.9%) | ⚠️ Leakage | EXCLUDED from features |
| 7 | Class imbalance (90:1) | 🔴 Critical | SMOTE + focal loss + threshold |
| 8 | Label noise (stated) | 🔴 Critical | Label smoothing + cleanlab |

### Limitations & Caveats

1. **20% Sample** — distributions may shift with full data
2. **Label Noise** — some findings may be artifacts of noisy labels
3. **Temporal Confounds** — mule behavior may evolve over the 5-year window (concept drift)
4. **Class Imbalance in EDA** — density-normalized plots used throughout
5. **Counterparty Opacity** — cannot distinguish accounts from merchants
6. **Geographic Coarseness** — PIN codes provide only coarse location

### Ethical AI Considerations

- ✅ Features avoid protected demographic attributes (age, geography) as primary predictors
- ✅ Model explainability (SHAP values) planned for Phase 2
- ✅ Threshold selection considers false-positive impact on legitimate customers
- ✅ Concept drift monitoring recommended for production

---

## 📁 Repository Structure

```
NFPC_Team_TETRINOX/
├── README.md                        # This file — comprehensive analysis documentation
├── NFPC_EDA_Report.pdf              # Full PDF report with all visualizations
├── NFPC_EDA_Notebook.ipynb          # Interactive Jupyter notebook (27 cells)
├── eda_report.md                    # Markdown version of the EDA report
│
├── generate_pdf.py                  # PDF report generator (1500+ lines)
├── create_notebook.py               # Notebook generator script
├── eda_full.py                      # Full EDA pipeline script
├── eda_part2.py                     # EDA Part 2 — Feature Engineering
├── eda_part3.py                     # EDA Part 3 — Modeling Strategy
├── eda_report.py                    # EDA report generation
├── restructure_pdf.py               # PDF restructuring utility
│
├── plots/                           # All EDA visualizations (14 PNG plots)
│   ├── target_distribution.png
│   ├── balance_distributions.png
│   ├── account_age_distribution.png
│   ├── customer_demographics.png
│   ├── digital_banking_adoption.png
│   ├── product_family_distribution.png
│   ├── txn_volume_distribution.png
│   ├── channel_usage.png
│   ├── temporal_patterns.png
│   ├── counterparty_diversity.png
│   ├── structuring_pattern.png
│   ├── branch_mule_concentration.png
│   ├── branch_analysis.png
│   └── mule_flagging_timeline.png
│
├── IITD-Tryst-Hackathon/            # Original hackathon data & guidelines
│   └── EDA-Phase-1/
│       ├── README.md
│       ├── EDA_GUIDE.md
│       ├── SUBMISSION_GUIDELINES.md
│       ├── accounts.csv
│       ├── customers.csv
│       ├── customer_account_linkage.csv
│       ├── product_details.csv
│       ├── train_labels.csv
│       ├── test_accounts.csv
│       └── transactions_part_[0-5].csv
│
├── dataset_info.txt                 # Dataset schema & null analysis
├── sections.txt                     # PDF section index
├── pdf1_content.txt                 # Challenge description (extracted)
├── pdf2_content.txt                 # Challenge overview (extracted)
├── pdf_error.txt                    # Debug log
└── eda_run_log.txt                  # EDA execution log
```

---

## 🚀 How to Reproduce

### Prerequisites

```bash
pip install pandas numpy matplotlib seaborn scikit-learn fpdf2 networkx
```

### Run the EDA

```bash
# Full EDA pipeline
python eda_full.py

# Generate PDF report
python generate_pdf.py

# Generate Jupyter notebook
python create_notebook.py
```

### Open the Notebook

```bash
jupyter notebook NFPC_EDA_Notebook.ipynb
```

---

<p align="center">
  <strong>🛡️ Built for the National Fraud Prevention Challenge (NFPC)</strong><br/>
  <em>Reserve Bank Innovation Hub (RBIH) × IIT Delhi TRYST</em><br/>
  <strong>Team TETRINOX</strong>
</p>
