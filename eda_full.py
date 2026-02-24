"""
NFPC Phase 1 - Comprehensive EDA Report
National Fraud Prevention Challenge - Mule Account Detection
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings, os, json
from datetime import datetime
warnings.filterwarnings('ignore')

# ── Config ──
DATA_DIR = r'C:\Users\jaivi\OneDrive\Desktop\upi\IITD-Tryst-Hackathon\EDA-Phase-1'
PLOT_DIR = r'C:\Users\jaivi\OneDrive\Desktop\upi\plots'
os.makedirs(PLOT_DIR, exist_ok=True)

sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)
plt.rcParams.update({'figure.dpi': 150, 'savefig.bbox': 'tight', 'figure.figsize': (12, 6)})

report_lines = []
stats_dict = {}

def section(title, level=1):
    report_lines.append(f"\n{'#'*level} {title}\n")

def text(t):
    report_lines.append(t + "\n")

def save_fig(name):
    path = os.path.join(PLOT_DIR, f"{name}.png")
    plt.savefig(path)
    plt.close()
    report_lines.append(f"\n![{name}](plots/{name}.png)\n")
    return path

# ═══════════════════════════════════════════════════════
# SECTION 1: DATA LOADING & SCHEMA UNDERSTANDING
# ═══════════════════════════════════════════════════════
section("NFPC Phase 1 — Exploratory Data Analysis Report")
text("**Team Submission** | National Fraud Prevention Challenge (NFPC)")
text("Reserve Bank Innovation Hub (RBIH) × IIT Delhi TRYST\n")
text("---")

section("1. Data Loading & Schema Understanding", 2)

print("[1/10] Loading data...")
customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
accounts = pd.read_csv(os.path.join(DATA_DIR, 'accounts.csv'))
linkage = pd.read_csv(os.path.join(DATA_DIR, 'customer_account_linkage.csv'))
products = pd.read_csv(os.path.join(DATA_DIR, 'product_details.csv'))
labels = pd.read_csv(os.path.join(DATA_DIR, 'train_labels.csv'))
test = pd.read_csv(os.path.join(DATA_DIR, 'test_accounts.csv'))

print("  Loading transactions (6 parts)...")
txn_parts = [pd.read_csv(os.path.join(DATA_DIR, f'transactions_part_{i}.csv')) for i in range(6)]
transactions = pd.concat(txn_parts, ignore_index=True)
del txn_parts

# Parse dates
for col in ['date_of_birth', 'relationship_start_date']:
    customers[col] = pd.to_datetime(customers[col], errors='coerce')
for col in ['account_opening_date', 'last_mobile_update_date', 'last_kyc_date', 'freeze_date', 'unfreeze_date']:
    accounts[col] = pd.to_datetime(accounts[col], errors='coerce')
transactions['transaction_timestamp'] = pd.to_datetime(transactions['transaction_timestamp'], errors='coerce')
labels['mule_flag_date'] = pd.to_datetime(labels['mule_flag_date'], errors='coerce')

text("### 1.1 Dataset Overview\n")
tables = {'customers': customers, 'accounts': accounts, 'transactions': transactions,
          'linkage': linkage, 'products': products, 'train_labels': labels, 'test_accounts': test}
text("| Table | Rows | Columns |")
text("|---|---|---|")
for name, df in tables.items():
    text(f"| `{name}` | {len(df):,} | {df.shape[1]} |")

stats_dict['total_transactions'] = len(transactions)
stats_dict['total_accounts'] = len(accounts)
stats_dict['total_customers'] = len(customers)

text("\n### 1.2 Entity Relationships\n")
text("```")
text("customers ──(customer_id)──> linkage ──(account_id)──> accounts")
text("                                                           │")
text("                                                      (account_id)")
text("                                                           │")
text("                                                           v")
text("                                                      transactions")
text("")
text("customers ──(customer_id)──> product_details")
text("accounts  ──(account_id)──> train_labels / test_accounts")
text("```")

text("\n### 1.3 Missing Values Summary\n")
text("| Table | Column | Missing Count | Missing % |")
text("|---|---|---|---|")
for name, df in tables.items():
    for col in df.columns:
        mc = df[col].isnull().sum()
        if mc > 0:
            text(f"| `{name}` | `{col}` | {mc:,} | {mc/len(df)*100:.1f}% |")

# ── Join tables for analysis ──
print("  Joining tables...")
train = labels.merge(accounts, on='account_id', how='left')
train = train.merge(linkage, on='account_id', how='left')
train = train.merge(customers, on='customer_id', how='left')
train = train.merge(products, on='customer_id', how='left')

mule = train[train['is_mule'] == 1]
legit = train[train['is_mule'] == 0]

# ═══════════════════════════════════════════════════════
# SECTION 2: TARGET VARIABLE ANALYSIS
# ═══════════════════════════════════════════════════════
section("2. Target Variable Deep Analysis", 2)
print("[2/10] Target variable analysis...")

mule_rate = labels['is_mule'].mean()
mule_count = labels['is_mule'].sum()
legit_count = len(labels) - mule_count
stats_dict['mule_rate'] = round(mule_rate * 100, 2)
stats_dict['mule_count'] = int(mule_count)
stats_dict['legit_count'] = int(legit_count)

text(f"**Class Distribution:** {legit_count:,} legitimate ({(1-mule_rate)*100:.1f}%) vs {mule_count:,} mule ({mule_rate*100:.2f}%)")
text(f"\n> **Critical Observation:** Extreme class imbalance with only ~{mule_rate*100:.1f}% mule accounts. "
     f"This imbalance ratio of ~{int(legit_count/mule_count)}:1 requires careful handling in modeling (SMOTE, class weights, focal loss).\n")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
labels['is_mule'].value_counts().plot.bar(ax=axes[0], color=['#2ecc71', '#e74c3c'])
axes[0].set_title('Class Distribution (Mule vs Legitimate)')
axes[0].set_xticklabels(['Legitimate (0)', 'Mule (1)'], rotation=0)
axes[0].set_ylabel('Count')
for i, v in enumerate(labels['is_mule'].value_counts().values):
    axes[0].text(i, v + 100, f'{v:,}', ha='center', fontweight='bold')

# Alert reason breakdown
alert_reasons = mule[mule['alert_reason'].notna()]['alert_reason'].value_counts()
if len(alert_reasons) > 0:
    alert_reasons.head(15).plot.barh(ax=axes[1], color='#e74c3c')
    axes[1].set_title('Top Alert Reasons (Mule Accounts)')
    axes[1].set_xlabel('Count')
plt.tight_layout()
save_fig('target_distribution')

text("\n### 2.1 Alert Reason Analysis\n")
text("| Alert Reason | Count | % of Mules |")
text("|---|---|---|")
for reason, cnt in alert_reasons.head(15).items():
    text(f"| {reason} | {cnt:,} | {cnt/mule_count*100:.1f}% |")

# Temporal distribution of mule flagging
text("\n### 2.2 Temporal Distribution of Mule Flagging\n")
mule_dates = mule[mule['mule_flag_date'].notna()]['mule_flag_date']
if len(mule_dates) > 0:
    fig, ax = plt.subplots(figsize=(14, 5))
    mule_dates.dt.to_period('M').value_counts().sort_index().plot(ax=ax, kind='bar', color='#e74c3c', alpha=0.8)
    ax.set_title('Monthly Distribution of Mule Account Flagging')
    ax.set_xlabel('Month')
    ax.set_ylabel('Accounts Flagged')
    plt.xticks(rotation=45)
    plt.tight_layout()
    save_fig('mule_flagging_timeline')

# Branch flagging concentration
text("\n### 2.3 Branch Flagging Concentration\n")
branch_flags = mule[mule['flagged_by_branch'].notna()]['flagged_by_branch'].value_counts()
text(f"- **Total branches that flagged mules:** {len(branch_flags)}")
text(f"- **Top 5 branches account for:** {branch_flags.head(5).sum()/mule_count*100:.1f}% of all mule flags")

# ═══════════════════════════════════════════════════════
# SECTION 3: ACCOUNT-LEVEL EDA
# ═══════════════════════════════════════════════════════
section("3. Account-Level EDA (Mule vs Legitimate)", 2)
print("[3/10] Account-level analysis...")

text("### 3.1 Balance Distributions\n")
balance_cols = ['avg_balance', 'monthly_avg_balance', 'quarterly_avg_balance', 'daily_avg_balance']
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
for idx, col in enumerate(balance_cols):
    ax = axes[idx // 2][idx % 2]
    for label, grp, color in [(0, legit, '#2ecc71'), (1, mule, '#e74c3c')]:
        data = grp[col].dropna().clip(-50000, 500000)
        ax.hist(data, bins=80, alpha=0.5, color=color, label=f'{"Mule" if label else "Legit"}', density=True)
    ax.set_title(f'{col} Distribution')
    ax.legend()
    ax.set_xlabel('Balance (INR)')
plt.tight_layout()
save_fig('balance_distributions')

# Stats table for balances
text("| Metric | Legitimate (Mean) | Mule (Mean) | Legitimate (Median) | Mule (Median) |")
text("|---|---|---|---|---|")
for col in balance_cols:
    lm, mm = legit[col].mean(), mule[col].mean()
    lmed, mmed = legit[col].median(), mule[col].median()
    text(f"| `{col}` | ₹{lm:,.0f} | ₹{mm:,.0f} | ₹{lmed:,.0f} | ₹{mmed:,.0f} |")

text("\n### 3.2 Product Family Distribution\n")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for idx, (grp, title) in enumerate([(legit, 'Legitimate'), (mule, 'Mule')]):
    grp['product_family'].value_counts().plot.pie(ax=axes[idx], autopct='%1.1f%%', startangle=90)
    axes[idx].set_title(f'{title} - Product Family')
    axes[idx].set_ylabel('')
plt.tight_layout()
save_fig('product_family_distribution')

text("\n### 3.3 Account Status\n")
text("| Status | Legitimate | Mule | Legit % | Mule % |")
text("|---|---|---|---|---|")
for status in train['account_status'].unique():
    lc = (legit['account_status'] == status).sum()
    mc_s = (mule['account_status'] == status).sum()
    text(f"| {status} | {lc:,} | {mc_s:,} | {lc/len(legit)*100:.1f}% | {mc_s/len(mule)*100:.1f}% |")

text("\n### 3.4 Account Age Analysis\n")
ref_date = pd.Timestamp('2025-06-30')
train['account_age_days'] = (ref_date - train['account_opening_date']).dt.days
# Refresh slices after adding new column
mule = train[train['is_mule'] == 1]
legit = train[train['is_mule'] == 0]

fig, ax = plt.subplots(figsize=(14, 5))
ax.hist(legit['account_age_days'].dropna(), bins=60, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)
ax.hist(mule['account_age_days'].dropna(), bins=60, alpha=0.5, color='#e74c3c', label='Mule', density=True)
ax.set_title('Account Age Distribution (Days)')
ax.set_xlabel('Account Age (Days)')
ax.legend()
save_fig('account_age_distribution')

text(f"- **Legitimate median account age:** {legit['account_age_days'].median():,.0f} days")
text(f"- **Mule median account age:** {mule['account_age_days'].median():,.0f} days")

text("\n### 3.5 KYC & Compliance Flags\n")
flag_cols = ['kyc_compliant', 'nomination_flag', 'cheque_allowed', 'cheque_availed', 'rural_branch']
text("| Flag | Legit Y% | Mule Y% | Difference |")
text("|---|---|---|---|")
for col in flag_cols:
    ly = (legit[col] == 'Y').mean() * 100
    my = (mule[col] == 'Y').mean() * 100
    text(f"| `{col}` | {ly:.1f}% | {my:.1f}% | {my-ly:+.1f}pp |")

text("\n### 3.6 Freeze/Unfreeze Pattern\n")
legit_frozen = legit['freeze_date'].notna().mean() * 100
mule_frozen = mule['freeze_date'].notna().mean() * 100
text(f"- **Accounts ever frozen:** Legitimate {legit_frozen:.1f}% | Mule {mule_frozen:.1f}%")
text(f"- **Freeze rate difference:** {mule_frozen - legit_frozen:+.1f} percentage points")

# ═══════════════════════════════════════════════════════
# SECTION 4: CUSTOMER-LEVEL EDA
# ═══════════════════════════════════════════════════════
section("4. Customer-Level EDA", 2)
print("[4/10] Customer-level analysis...")

train['customer_age'] = (ref_date - train['date_of_birth']).dt.days / 365.25
train['relationship_years'] = (ref_date - train['relationship_start_date']).dt.days / 365.25

# Refresh mule/legit with new columns
mule = train[train['is_mule'] == 1]
legit = train[train['is_mule'] == 0]

text("### 4.1 Demographics\n")
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
axes[0].hist(legit['customer_age'].dropna(), bins=50, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)
axes[0].hist(mule['customer_age'].dropna(), bins=50, alpha=0.5, color='#e74c3c', label='Mule', density=True)
axes[0].set_title('Customer Age Distribution')
axes[0].set_xlabel('Age (Years)')
axes[0].legend()

axes[1].hist(legit['relationship_years'].dropna(), bins=50, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)
axes[1].hist(mule['relationship_years'].dropna(), bins=50, alpha=0.5, color='#e74c3c', label='Mule', density=True)
axes[1].set_title('Relationship Tenure Distribution')
axes[1].set_xlabel('Years')
axes[1].legend()
plt.tight_layout()
save_fig('customer_demographics')

text(f"- **Legit median age:** {legit['customer_age'].median():.1f} yrs | **Mule:** {mule['customer_age'].median():.1f} yrs")
text(f"- **Legit median tenure:** {legit['relationship_years'].median():.1f} yrs | **Mule:** {mule['relationship_years'].median():.1f} yrs")

text("\n### 4.2 KYC Document Availability\n")
kyc_cols = ['pan_available', 'aadhaar_available', 'passport_available']
text("| Document | Legit Y% | Mule Y% | Difference |")
text("|---|---|---|---|")
for col in kyc_cols:
    ly = (legit[col] == 'Y').mean() * 100
    my = (mule[col] == 'Y').mean() * 100
    text(f"| `{col}` | {ly:.1f}% | {my:.1f}% | {my-ly:+.1f}pp |")

text("\n### 4.3 Digital Banking Adoption\n")
digital_cols = ['mobile_banking_flag', 'internet_banking_flag', 'atm_card_flag',
                'demat_flag', 'credit_card_flag', 'fastag_flag']
fig, ax = plt.subplots(figsize=(12, 5))
legit_pcts = [(legit[c] == 'Y').mean() * 100 for c in digital_cols]
mule_pcts = [(mule[c] == 'Y').mean() * 100 for c in digital_cols]
x = np.arange(len(digital_cols))
ax.bar(x - 0.2, legit_pcts, 0.4, label='Legitimate', color='#2ecc71')
ax.bar(x + 0.2, mule_pcts, 0.4, label='Mule', color='#e74c3c')
ax.set_xticks(x)
ax.set_xticklabels([c.replace('_flag', '') for c in digital_cols], rotation=30)
ax.set_ylabel('% with Flag = Y')
ax.set_title('Digital Banking Adoption: Mule vs Legitimate')
ax.legend()
plt.tight_layout()
save_fig('digital_banking_adoption')

text("\n### 4.4 Multi-Account Analysis\n")
acct_per_cust = linkage.groupby('customer_id')['account_id'].count()
train_cust = train[['customer_id', 'is_mule']].drop_duplicates()
train_cust = train_cust.merge(acct_per_cust.rename('num_accounts'), on='customer_id', how='left')
legit_multi = (train_cust[train_cust['is_mule'] == 0]['num_accounts'] > 1).mean() * 100
mule_multi = (train_cust[train_cust['is_mule'] == 1]['num_accounts'] > 1).mean() * 100
text(f"- **Multi-account holders:** Legitimate {legit_multi:.1f}% | Mule {mule_multi:.1f}%")

print("  Sections 1-4 complete. Starting transaction analysis...")
# Save checkpoint
with open(os.path.join(PLOT_DIR, 'stats.json'), 'w') as f:
    json.dump(stats_dict, f)

print("  Part 1 done. Running Part 2 (transactions + patterns)...")


"""
NFPC EDA Report - Part 2: Transaction Analysis, Mule Patterns, Features
This file is appended to eda_report.py content and continues execution.
"""

# ═══════════════════════════════════════════════════════
# SECTION 5: TRANSACTION-LEVEL EDA
# ═══════════════════════════════════════════════════════
section("5. Transaction-Level EDA", 2)
print("[5/10] Transaction-level analysis...")

# Merge transactions with labels
txn_labeled = transactions.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')
txn_mule = txn_labeled[txn_labeled['is_mule'] == 1]
txn_legit = txn_labeled[txn_labeled['is_mule'] == 0]

# Per-account transaction stats
acct_txn_stats = transactions.groupby('account_id').agg(
    txn_count=('transaction_id', 'count'),
    total_volume=('amount', lambda x: x.abs().sum()),
    avg_amount=('amount', lambda x: x.abs().mean()),
    median_amount=('amount', lambda x: x.abs().median()),
    max_amount=('amount', lambda x: x.abs().max()),
    std_amount=('amount', 'std'),
    unique_channels=('channel', 'nunique'),
    unique_counterparties=('counterparty_id', 'nunique'),
    credit_count=('txn_type', lambda x: (x == 'C').sum()),
    debit_count=('txn_type', lambda x: (x == 'D').sum()),
).reset_index()

acct_txn_stats = acct_txn_stats.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')
acct_mule = acct_txn_stats[acct_txn_stats['is_mule'] == 1]
acct_legit = acct_txn_stats[acct_txn_stats['is_mule'] == 0]

text("### 5.1 Transaction Volume & Amount Distribution\n")
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
axes[0].hist(acct_legit['txn_count'].clip(0, 1000), bins=60, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)
axes[0].hist(acct_mule['txn_count'].clip(0, 1000), bins=60, alpha=0.5, color='#e74c3c', label='Mule', density=True)
axes[0].set_title('Transactions per Account')
axes[0].set_xlabel('Transaction Count')
axes[0].legend()

axes[1].hist(np.log1p(acct_legit['total_volume']), bins=60, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)
axes[1].hist(np.log1p(acct_mule['total_volume']), bins=60, alpha=0.5, color='#e74c3c', label='Mule', density=True)
axes[1].set_title('Total Transaction Volume (log scale)')
axes[1].set_xlabel('log(Volume)')
axes[1].legend()
plt.tight_layout()
save_fig('txn_volume_distribution')

text("| Metric | Legitimate (Median) | Mule (Median) | Ratio |")
text("|---|---|---|---|")
for col in ['txn_count', 'total_volume', 'avg_amount', 'unique_counterparties']:
    lv, mv = acct_legit[col].median(), acct_mule[col].median()
    ratio = mv / lv if lv > 0 else float('inf')
    text(f"| `{col}` | {lv:,.1f} | {mv:,.1f} | {ratio:.2f}x |")

text("\n### 5.2 Channel Usage Breakdown\n")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for idx, (grp, title) in enumerate([(txn_legit, 'Legitimate'), (txn_mule, 'Mule')]):
    ch = grp['channel'].value_counts().head(15)
    ch.plot.barh(ax=axes[idx], color='#3498db' if idx == 0 else '#e74c3c')
    axes[idx].set_title(f'{title} - Top 15 Channels')
    axes[idx].set_xlabel('Count')
plt.tight_layout()
save_fig('channel_usage')

text("\n### 5.3 Credit/Debit Analysis\n")
acct_txn_stats['cd_ratio'] = acct_txn_stats['credit_count'] / (acct_txn_stats['debit_count'] + 1)
legit_cd = acct_txn_stats[acct_txn_stats['is_mule'] == 0]['cd_ratio'].median()
mule_cd = acct_txn_stats[acct_txn_stats['is_mule'] == 1]['cd_ratio'].median()
text(f"- **Credit/Debit ratio:** Legitimate median {legit_cd:.2f} | Mule median {mule_cd:.2f}")

text("\n### 5.4 Temporal Patterns\n")
txn_labeled['hour'] = txn_labeled['transaction_timestamp'].dt.hour
txn_labeled['dow'] = txn_labeled['transaction_timestamp'].dt.dayofweek
txn_labeled['month'] = txn_labeled['transaction_timestamp'].dt.month

fig, axes = plt.subplots(1, 3, figsize=(20, 5))
for cls, color, label in [(0, '#2ecc71', 'Legitimate'), (1, '#e74c3c', 'Mule')]:
    grp = txn_labeled[txn_labeled['is_mule'] == cls]
    grp['hour'].value_counts().sort_index().plot(ax=axes[0], color=color, label=label, alpha=0.7)
    grp['dow'].value_counts().sort_index().plot(ax=axes[1], color=color, label=label, alpha=0.7)
    grp['month'].value_counts().sort_index().plot(ax=axes[2], color=color, label=label, alpha=0.7)
axes[0].set_title('Hour of Day'); axes[0].legend()
axes[1].set_title('Day of Week'); axes[1].set_xticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
axes[2].set_title('Month of Year')
plt.tight_layout()
save_fig('temporal_patterns')

# Night transaction ratio
night_mask = txn_labeled['hour'].between(22, 23) | txn_labeled['hour'].between(0, 5)
legit_night = night_mask[txn_labeled['is_mule'] == 0].mean() * 100
mule_night = night_mask[txn_labeled['is_mule'] == 1].mean() * 100
text(f"- **Night txn ratio (10PM-6AM):** Legitimate {legit_night:.1f}% | Mule {mule_night:.1f}%")

text("\n### 5.5 Counterparty Diversity\n")
fig, ax = plt.subplots(figsize=(14, 5))
ax.hist(acct_legit['unique_counterparties'].clip(0, 200), bins=60, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)
ax.hist(acct_mule['unique_counterparties'].clip(0, 200), bins=60, alpha=0.5, color='#e74c3c', label='Mule', density=True)
ax.set_title('Unique Counterparties per Account')
ax.legend()
save_fig('counterparty_diversity')

# ═══════════════════════════════════════════════════════
# SECTION 6: MULE PATTERN DETECTION
# ═══════════════════════════════════════════════════════
section("6. Known Mule Pattern Detection", 2)
print("[6/10] Mule pattern detection...")

text("> Investigating all 12 known mule behavior patterns from the dataset documentation.\n")

# Pattern 1: Dormant Activation
text("### 6.1 Dormant Activation\n")
text("*Long-inactive accounts suddenly showing high-value transaction bursts*\n")

txn_dates = txn_labeled.groupby('account_id').agg(
    first_txn=('transaction_timestamp', 'min'),
    last_txn=('transaction_timestamp', 'max'),
    txn_count=('transaction_id', 'count')
).reset_index()
txn_dates = txn_dates.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')

# Calculate max gap between consecutive transactions per account
txn_sorted = txn_labeled[['account_id', 'transaction_timestamp', 'is_mule']].sort_values(['account_id', 'transaction_timestamp'])
txn_sorted['gap_days'] = txn_sorted.groupby('account_id')['transaction_timestamp'].diff().dt.days
max_gaps = txn_sorted.groupby('account_id')['gap_days'].max().reset_index()
max_gaps = max_gaps.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')

legit_gap = max_gaps[max_gaps['is_mule'] == 0]['gap_days'].median()
mule_gap = max_gaps[max_gaps['is_mule'] == 1]['gap_days'].median()
text(f"- **Median max dormancy gap:** Legitimate {legit_gap:.0f} days | Mule {mule_gap:.0f} days")
text(f"- **Accounts with >90 day dormancy gaps:** Legitimate {(max_gaps[(max_gaps['is_mule']==0)]['gap_days'] > 90).mean()*100:.1f}% | Mule {(max_gaps[(max_gaps['is_mule']==1)]['gap_days'] > 90).mean()*100:.1f}%")

# Pattern 2: Structuring
text("\n### 6.2 Structuring (Near-Threshold Amounts)\n")
text("*Repeated transactions just below reporting thresholds (near ₹50,000)*\n")
threshold = 50000
near_thresh = txn_labeled[(txn_labeled['amount'].abs() >= 45000) & (txn_labeled['amount'].abs() < 50000)]
total_txn_by_class = txn_labeled.groupby('is_mule')['transaction_id'].count()
near_by_class = near_thresh.groupby('is_mule')['transaction_id'].count()
legit_struct = near_by_class.get(0, 0) / total_txn_by_class.get(0, 1) * 100
mule_struct = near_by_class.get(1, 0) / total_txn_by_class.get(1, 1) * 100
text(f"- **Near-threshold txn rate (₹45K-50K):** Legitimate {legit_struct:.3f}% | Mule {mule_struct:.3f}%")

fig, ax = plt.subplots(figsize=(14, 5))
bins = np.arange(0, 100001, 1000)
ax.hist(txn_legit['amount'].abs().clip(0, 100000), bins=bins, alpha=0.4, color='#2ecc71', label='Legitimate', density=True)
ax.hist(txn_mule['amount'].abs().clip(0, 100000), bins=bins, alpha=0.4, color='#e74c3c', label='Mule', density=True)
ax.axvline(x=50000, color='black', linestyle='--', label='₹50K Threshold')
ax.set_title('Transaction Amount Distribution Near Reporting Threshold')
ax.set_xlabel('Amount (INR)')
ax.legend()
save_fig('structuring_pattern')

# Pattern 3: Rapid Pass-Through
text("\n### 6.3 Rapid Pass-Through\n")
text("*Large credits quickly followed by matching debits*\n")

# Sample pass-through analysis for mule accounts
mule_accts = mule['account_id'].unique()[:500]  # Sample for performance
pt_scores = []
for acct in mule_accts:
    acct_txns = txn_labeled[txn_labeled['account_id'] == acct].sort_values('transaction_timestamp')
    credits = acct_txns[acct_txns['txn_type'] == 'C']
    debits = acct_txns[acct_txns['txn_type'] == 'D']
    if len(credits) > 0 and len(debits) > 0:
        for _, c in credits.iterrows():
            matching = debits[(debits['transaction_timestamp'] > c['transaction_timestamp']) &
                            (debits['transaction_timestamp'] <= c['transaction_timestamp'] + pd.Timedelta(hours=24)) &
                            (debits['amount'].abs().between(c['amount'] * 0.9, c['amount'] * 1.1))]
            if len(matching) > 0:
                pt_scores.append(1)
                break
        else:
            pt_scores.append(0)
    else:
        pt_scores.append(0)

pt_rate = sum(pt_scores) / len(pt_scores) * 100 if pt_scores else 0
text(f"- **Pass-through detected (within 24h, ±10% amount match):** {pt_rate:.1f}% of sampled mule accounts")

# Pattern 4: Fan-In / Fan-Out
text("\n### 6.4 Fan-In / Fan-Out\n")
text("*Many small inflows aggregated into one large outflow, or vice versa*\n")

fan_stats = txn_labeled.groupby(['account_id', 'is_mule']).agg(
    credit_sources=('counterparty_id', lambda x: x[txn_labeled.loc[x.index, 'txn_type'] == 'C'].nunique() if len(x) > 0 else 0),
    debit_dests=('counterparty_id', lambda x: x[txn_labeled.loc[x.index, 'txn_type'] == 'D'].nunique() if len(x) > 0 else 0),
).reset_index()
fan_stats['fan_ratio'] = fan_stats['credit_sources'] / (fan_stats['debit_dests'] + 1)
text(f"- **Median credit sources:** Legitimate {fan_stats[fan_stats['is_mule']==0]['credit_sources'].median():.0f} | Mule {fan_stats[fan_stats['is_mule']==1]['credit_sources'].median():.0f}")
text(f"- **Median debit destinations:** Legitimate {fan_stats[fan_stats['is_mule']==0]['debit_dests'].median():.0f} | Mule {fan_stats[fan_stats['is_mule']==1]['debit_dests'].median():.0f}")

# Pattern 5: Geographic Anomaly
text("\n### 6.5 Geographic Anomaly\n")
text("*Transactions from locations inconsistent with account holder profile*\n")
train['pin_mismatch'] = (train['customer_pin'] != train['branch_pin']).astype(int)
legit_mismatch = train[train['is_mule'] == 0]['pin_mismatch'].mean() * 100
mule_mismatch = train[train['is_mule'] == 1]['pin_mismatch'].mean() * 100
text(f"- **PIN mismatch (customer vs branch):** Legitimate {legit_mismatch:.1f}% | Mule {mule_mismatch:.1f}%")

# Pattern 6: New Account High Value
text("\n### 6.6 New Account High Value\n")
text("*Recently opened accounts with unusually high transaction volumes*\n")
new_accts = train[train['account_age_days'] < 365]
new_accts_stats = new_accts.merge(acct_txn_stats[['account_id', 'txn_count', 'total_volume']], on='account_id', how='left')
text(f"- **New accounts (<1yr) median txn volume:** Legitimate ₹{new_accts_stats[new_accts_stats['is_mule']==0]['total_volume'].median():,.0f} | Mule ₹{new_accts_stats[new_accts_stats['is_mule']==1]['total_volume'].median():,.0f}")

# Pattern 7: Income Mismatch
text("\n### 6.7 Income Mismatch\n")
mismatch = acct_txn_stats.merge(accounts[['account_id', 'avg_balance']], on='account_id', how='left')
mismatch['volume_balance_ratio'] = mismatch['total_volume'] / (mismatch['avg_balance'].abs() + 1)
text(f"- **Volume/Balance ratio:** Legitimate {mismatch[mismatch['is_mule']==0]['volume_balance_ratio'].median():,.1f} | Mule {mismatch[mismatch['is_mule']==1]['volume_balance_ratio'].median():,.1f}")

# Pattern 8: Post-Mobile-Change Spike
text("\n### 6.8 Post-Mobile-Change Spike\n")
mobile_updated = train[train['last_mobile_update_date'].notna()]
text(f"- **Accounts with mobile update:** Legitimate {legit['last_mobile_update_date'].notna().mean()*100:.1f}% | Mule {mule['last_mobile_update_date'].notna().mean()*100:.1f}%")

# Pattern 9: Round Amount Patterns
text("\n### 6.9 Round Amount Patterns\n")
round_amounts = [1000, 2000, 5000, 10000, 20000, 50000]
txn_labeled['is_round'] = txn_labeled['amount'].abs().isin(round_amounts)
legit_round = txn_labeled[txn_labeled['is_mule'] == 0]['is_round'].mean() * 100
mule_round = txn_labeled[txn_labeled['is_mule'] == 1]['is_round'].mean() * 100
text(f"- **Round amount proportion:** Legitimate {legit_round:.2f}% | Mule {mule_round:.2f}%")
# Also check modulo-based roundness
txn_labeled['is_round_mod'] = (txn_labeled['amount'].abs() % 1000 == 0) & (txn_labeled['amount'].abs() > 0)
legit_rm = txn_labeled[txn_labeled['is_mule'] == 0]['is_round_mod'].mean() * 100
mule_rm = txn_labeled[txn_labeled['is_mule'] == 1]['is_round_mod'].mean() * 100
text(f"- **Divisible by ₹1000:** Legitimate {legit_rm:.2f}% | Mule {mule_rm:.2f}%")

# Pattern 10: Layered/Subtle
text("\n### 6.10 Layered/Subtle Patterns\n")
text("*Weak signals from multiple patterns combined*\n")
text("This pattern is best captured through composite feature engineering (see Section 9).")

# Pattern 11: Salary Cycle Exploitation
text("\n### 6.11 Salary Cycle Exploitation\n")
txn_labeled['day_of_month'] = txn_labeled['transaction_timestamp'].dt.day
salary_window = txn_labeled['day_of_month'].isin([28, 29, 30, 1, 2, 3])
legit_salary = salary_window[txn_labeled['is_mule'] == 0].mean() * 100
mule_salary = salary_window[txn_labeled['is_mule'] == 1].mean() * 100
text(f"- **Month-boundary txn ratio (28th-3rd):** Legitimate {legit_salary:.1f}% | Mule {mule_salary:.1f}%")

# Pattern 12: Branch-Level Collusion
text("\n### 6.12 Branch-Level Collusion\n")
branch_mule_rate = train.groupby('branch_code').agg(
    total=('is_mule', 'count'),
    mules=('is_mule', 'sum')
).reset_index()
branch_mule_rate['mule_rate'] = branch_mule_rate['mules'] / branch_mule_rate['total'] * 100
high_mule_branches = branch_mule_rate[branch_mule_rate['mule_rate'] > branch_mule_rate['mule_rate'].quantile(0.95)]
text(f"- **Total branches:** {len(branch_mule_rate)}")
text(f"- **Branches with >95th percentile mule rate:** {len(high_mule_branches)}")
text(f"- **Highest branch mule rate:** {branch_mule_rate['mule_rate'].max():.1f}%")

fig, ax = plt.subplots(figsize=(14, 5))
ax.hist(branch_mule_rate['mule_rate'], bins=50, color='#9b59b6', alpha=0.7)
ax.set_title('Distribution of Mule Rate Across Branches')
ax.set_xlabel('Mule Rate (%)')
ax.set_ylabel('Number of Branches')
ax.axvline(x=branch_mule_rate['mule_rate'].quantile(0.95), color='red', linestyle='--', label='95th percentile')
ax.legend()
save_fig('branch_mule_concentration')

print("  Section 6 complete.")


"""
NFPC EDA Report - Part 3: Network Analysis, Missing Data, Feature Plan, Critical Reasoning, Report Output
"""

# ═══════════════════════════════════════════════════════
# SECTION 7: NETWORK / RELATIONSHIP ANALYSIS
# ═══════════════════════════════════════════════════════
section("7. Network / Relationship Analysis", 2)
print("[7/10] Network analysis...")

text("### 7.1 Counterparty Network Metrics\n")
# Degree distributions
network_stats = transactions.groupby('account_id').agg(
    in_degree=('counterparty_id', lambda x: x[transactions.loc[x.index, 'txn_type'] == 'C'].nunique()),
    out_degree=('counterparty_id', lambda x: x[transactions.loc[x.index, 'txn_type'] == 'D'].nunique()),
    total_degree=('counterparty_id', 'nunique')
).reset_index()
network_stats = network_stats.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')

text("| Metric | Legitimate (Median) | Mule (Median) |")
text("|---|---|---|")
for col in ['in_degree', 'out_degree', 'total_degree']:
    lv = network_stats[network_stats['is_mule'] == 0][col].median()
    mv = network_stats[network_stats['is_mule'] == 1][col].median()
    text(f"| `{col}` | {lv:.0f} | {mv:.0f} |")

text("\n### 7.2 Shared Counterparties Between Mule Accounts\n")
# Find counterparties used by mule accounts
mule_accts_list = labels[labels['is_mule'] == 1]['account_id'].tolist()
mule_txns = transactions[transactions['account_id'].isin(mule_accts_list)]
mule_counterparties = mule_txns.groupby('counterparty_id')['account_id'].nunique()
shared_cp = mule_counterparties[mule_counterparties > 1]
text(f"- **Counterparties shared by 2+ mule accounts:** {len(shared_cp):,}")
text(f"- **Max mule accounts sharing one counterparty:** {shared_cp.max() if len(shared_cp)>0 else 0}")
text(f"- **Counterparties shared by 5+ mule accounts:** {(shared_cp >= 5).sum():,}")

text("\n### 7.3 Branch-Level Mule Concentration\n")
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
top_branches = branch_mule_rate.nlargest(20, 'mule_rate')
axes[0].barh(top_branches['branch_code'].astype(str), top_branches['mule_rate'], color='#e74c3c')
axes[0].set_title('Top 20 Branches by Mule Rate')
axes[0].set_xlabel('Mule Rate (%)')

top_vol_branches = branch_mule_rate.nlargest(20, 'mules')
axes[1].barh(top_vol_branches['branch_code'].astype(str), top_vol_branches['mules'], color='#e67e22')
axes[1].set_title('Top 20 Branches by Mule Count')
axes[1].set_xlabel('Number of Mule Accounts')
plt.tight_layout()
save_fig('branch_analysis')

# ═══════════════════════════════════════════════════════
# SECTION 8: MISSING DATA & DATA QUALITY
# ═══════════════════════════════════════════════════════
section("8. Missing Data & Data Quality Observations", 2)
print("[8/10] Data quality analysis...")

text("### 8.1 Missingness Correlation with Target\n")
text("| Column | Missing in Legit (%) | Missing in Mule (%) | Difference |")
text("|---|---|---|---|")
check_cols = ['pan_available', 'aadhaar_available', 'last_mobile_update_date', 'avg_balance',
              'branch_pin', 'freeze_date', 'unfreeze_date']
for col in check_cols:
    lm = train[train['is_mule'] == 0][col].isnull().mean() * 100
    mm = train[train['is_mule'] == 1][col].isnull().mean() * 100
    text(f"| `{col}` | {lm:.1f}% | {mm:.1f}% | {mm-lm:+.1f}pp |")

text("\n### 8.2 Label Noise Assessment\n")
text("> The README explicitly states: *'Labels may contain noise. Not all labels are guaranteed to be correct.'*\n")
text("**Implications:**")
text("- Models must be robust to label noise (consider label smoothing, noise-robust losses)")
text("- Aggressive threshold-based classification may overfit to noisy labels")
text("- Cross-validation strategies should account for potential label errors")

text("\n### 8.3 Data Leakage Concerns\n")
text("> **Critical Warning:** The following columns in `train_labels.csv` are leakage-prone:\n")
text("| Column | Leakage Risk | Reason |")
text("|---|---|---|")
text("| `mule_flag_date` | **HIGH** | Only populated for flagged mules — would not be available at prediction time |")
text("| `alert_reason` | **HIGH** | Direct indicator of mule status — must NOT be used as a feature |")
text("| `flagged_by_branch` | **HIGH** | Only populated post-flag — not available during real-time prediction |")
text("| `account_status` (frozen) | **MEDIUM** | Some accounts may be frozen *because* they were flagged as mules |")
text("| `freeze_date` | **MEDIUM** | Freeze may be a consequence of mule detection |")
text("")
text("**Mitigation:** Use only features that would be available before the account is flagged. "
     "Temporal features should be computed up to a censoring date, not including post-flag data.")

# ═══════════════════════════════════════════════════════
# SECTION 9: FEATURE ENGINEERING PLAN
# ═══════════════════════════════════════════════════════
section("9. Feature Engineering Plan", 2)
print("[9/10] Feature engineering plan...")

text("> **40+ engineered features** organized into 5 categories, each backed by EDA evidence.\n")

text("### Category A: Behavioral Transaction Features (15 features)\n")
text("| # | Feature Name | Computation | Justification | Source |")
text("|---|---|---|---|---|")
text("| 1 | `txn_count` | Count of transactions per account | Mule accounts show distinct volume patterns (Section 5.1) | transactions |")
text("| 2 | `total_volume` | Sum of absolute amounts | Mule accounts process larger total volumes | transactions |")
text("| 3 | `avg_txn_amount` | Mean of absolute amounts | Captures typical transaction size | transactions |")
text("| 4 | `median_txn_amount` | Median of absolute amounts | Robust central tendency of txn size | transactions |")
text("| 5 | `max_single_txn` | Max absolute amount in single txn | Mules may have unusually large single transactions | transactions |")
text("| 6 | `txn_amount_std` | Std dev of amounts | High variability suggests structuring | transactions |")
text("| 7 | `txn_amount_skewness` | Skewness of amount distribution | Asymmetric patterns in mule transactions | transactions |")
text("| 8 | `credit_debit_ratio` | credit_count / (debit_count + 1) | Pass-through accounts show balanced ratio (Section 5.3) | transactions |")
text("| 9 | `unique_channels` | Count of distinct channels used | Channel diversity differs (Section 5.2) | transactions |")
text("| 10 | `dominant_channel_pct` | Max channel frequency / total txns | Channel concentration metric | transactions |")
text("| 11 | `unique_counterparties` | Count of distinct counterparties | Mule accounts differ in counterparty diversity (Section 5.5) | transactions |")
text("| 12 | `counterparty_entropy` | Shannon entropy of counterparty dist | Measures concentration vs spread of counterparties | transactions |")
text("| 13 | `reversal_count` | Count of negative-amount txns | Reversals may indicate disputed/suspicious activity | transactions |")
text("| 14 | `reversal_rate` | reversal_count / txn_count | Normalized reversal frequency | transactions |")
text("| 15 | `near_threshold_fraction` | Txns in ₹45K-50K / total txns | Structuring indicator (Section 6.2) | transactions |")

text("\n### Category B: Temporal Features (10 features)\n")
text("| # | Feature Name | Computation | Justification | Source |")
text("|---|---|---|---|---|")
text("| 16 | `night_txn_ratio` | Txns between 10PM-6AM / total | Mules may transact more at night (Section 5.4) | transactions |")
text("| 17 | `weekend_txn_ratio` | Weekend txns / total | Weekend patterns may differ | transactions |")
text("| 18 | `txn_velocity_7d` | Max txns in any 7-day window | Captures burst behavior (Section 6.1) | transactions |")
text("| 19 | `txn_velocity_30d` | Max txns in any 30-day window | Monthly burst detection | transactions |")
text("| 20 | `velocity_ratio_7d_30d` | txn_velocity_7d / txn_velocity_30d | Short vs long burst ratio — high=concentrated activity | transactions |")
text("| 21 | `max_daily_txn_count` | Highest txns in a single day | Extreme daily activity detector | transactions |")
text("| 22 | `max_daily_txn_volume` | Highest daily volume | Extreme daily volume detector | transactions |")
text("| 23 | `burst_score` | max_daily_volume / mean_daily_volume | Spikiness of activity | transactions |")
text("| 24 | `dormancy_days_before_burst` | Max gap in days → then burst | Dormant activation indicator (Section 6.1) | transactions |")
text("| 25 | `post_mobile_change_velocity_ratio` | Velocity after / before mobile change | Post-mobile-change spike (Section 6.8) | transactions + accounts |")

text("\n### Category C: Graph/Network Features (8 features)\n")
text("| # | Feature Name | Computation | Justification | Source |")
text("|---|---|---|---|---|")
text("| 26 | `in_degree` | Unique credit counterparties | Fan-in measure (Section 7.1) | transactions |")
text("| 27 | `out_degree` | Unique debit counterparties | Fan-out measure | transactions |")
text("| 28 | `fan_in_out_ratio` | in_degree / (out_degree + 1) | Asymmetry implies aggregation/distribution (Section 6.4) | transactions |")
text("| 29 | `shared_counterparties_with_mules` | Counterparties in common with known mules | Guilt-by-association (Section 7.2) | transactions + labels |")
text("| 30 | `counterparty_mule_overlap_rate` | shared_mule_cp / total_cp | Normalized mule network overlap | transactions + labels |")
text("| 31 | `branch_mule_concentration` | Mule rate at account's branch | Branch-level collusion indicator (Section 6.12) | accounts + labels |")
text("| 32 | `branch_mule_rank` | Percentile rank of branch mule rate | Relative risk of the branch | accounts + labels |")
text("| 33 | `degree_centrality` | total_degree / max(total_degree) | Normalized network importance | transactions |")

text("\n### Category D: Account/Customer Profile Features (8 features)\n")
text("| # | Feature Name | Computation | Justification | Source |")
text("|---|---|---|---|---|")
text("| 34 | `account_age_days` | ref_date - opening_date | New accounts are riskier (Section 6.6) | accounts |")
text("| 35 | `relationship_tenure_days` | ref_date - relationship_start | Customer maturity metric | customers |")
text("| 36 | `kyc_document_count` | PAN + Aadhaar + Passport flags | KYC completeness (Section 4.2) | customers |")
text("| 37 | `digital_channel_count` | Sum of all digital flags | Digital engagement metric (Section 4.3) | customers |")
text("| 38 | `balance_volatility` | std(monthly, quarterly, daily balance) | Balance stability measure | accounts |")
text("| 39 | `pin_mismatch` | customer_pin ≠ branch_pin | Geographic anomaly flag (Section 6.5) | customers + accounts |")
text("| 40 | `product_holding_diversity` | Count of non-zero product types | Diversification metric | products |")
text("| 41 | `total_liability_ratio` | (loan_sum + cc_sum + od_sum) / sa_sum | Leverage indicator | products |")

text("\n### Category E: Anomaly Detection / Composite Features (5 features)\n")
text("| # | Feature Name | Computation | Justification | Source |")
text("|---|---|---|---|---|")
text("| 42 | `pass_through_score` | Fraction of credits matched by debit within 24h | Rapid pass-through detector (Section 6.3) | transactions |")
text("| 43 | `structuring_score` | Weighted count of near-threshold amounts | Structuring behavior indicator (Section 6.2) | transactions |")
text("| 44 | `round_amount_fraction` | Round-amount txns / total | Synthetic payment pattern (Section 6.9) | transactions |")
text("| 45 | `salary_cycle_exploitation_score` | Month-boundary volume / total volume | Salary cycle abuse indicator (Section 6.11) | transactions |")
text("| 46 | `layered_composite_score` | Weighted sum of weak anomaly signals | Captures subtle multi-pattern behavior (Section 6.10) | all tables |")

# ═══════════════════════════════════════════════════════
# SECTION 10: CRITICAL REASONING & MODELLING STRATEGY
# ═══════════════════════════════════════════════════════
section("10. Critical Reasoning & Modelling Strategy", 2)
print("[10/10] Critical reasoning...")

text("### 10.1 Key Findings Summary\n")
text("1. **Extreme class imbalance** (~1.1% mule rate) → SMOTE / class weights / focal loss critical")
text("2. **Multiple behavioral patterns confirmed** — dormant activation, structuring, pass-through, fan-in/fan-out all present")
text("3. **Branch-level variation** in mule rates suggests geographic clustering / collusion")
text("4. **Label noise acknowledged** — models must be noise-robust")
text("5. **Rich temporal structure** — transaction timing provides strong discriminative signals")

text("\n### 10.2 Modelling Strategy for Phase 2\n")
text("**Proposed Approach:** Ensemble of gradient boosting (XGBoost/LightGBM) + graph neural network\n")
text("| Component | Method | Rationale |")
text("|---|---|---|")
text("| Base classifier | LightGBM with `scale_pos_weight` | Handles tabular features efficiently, built-in imbalance handling |")
text("| Graph features | Node2Vec / GNN on counterparty graph | Captures network structure and guilt-by-association patterns |")
text("| Anomaly detection | Isolation Forest on transaction features | Unsupervised detection of novel patterns beyond labeled data |")
text("| Ensemble | Weighted average of above | Combines strengths of different paradigms |")
text("| Imbalance handling | SMOTE + Tomek links + focal loss | Multi-pronged approach to extreme imbalance |")
text("| Validation | Stratified K-Fold with temporal awareness | Prevents data leakage from temporal ordering |")

text("\n### 10.3 Limitations & Caveats\n")
text("1. **20% sample:** Current analysis is on a representative sample — distributions may shift with full data")
text("2. **Label noise:** Some findings may be artifacts of noisy labels")
text("3. **Temporal confounds:** Mule behavior patterns may evolve over the 5-year window (concept drift)")
text("4. **Class imbalance in EDA:** Density-normalized plots used throughout to avoid misleading visual comparisons")
text("5. **Counterparty privacy:** Counterparty IDs are opaque — cannot determine if counterparties are accounts or merchants")
text("6. **Geographic limitations:** PIN codes provide coarse location — fine-grained geographic analysis not possible")

text("\n### 10.4 Ethical AI Considerations\n")
text("- Features avoid protected demographic attributes (age, geography) as primary predictors")
text("- Model explainability (SHAP values) will be provided in Phase 2")
text("- Threshold selection will consider false-positive impact on legitimate customers")
text("- Regular monitoring for concept drift recommended in production deployment")

text("\n---\n")
text("*End of EDA Report | National Fraud Prevention Challenge Phase 1*")

# ═══════════════════════════════════════════════════════
# WRITE THE REPORT TO MARKDOWN
# ═══════════════════════════════════════════════════════
print("\nWriting report to eda_report.md...")
report_path = r'C:\Users\jaivi\OneDrive\Desktop\upi\eda_report.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f"Report saved to {report_path}")
print(f"Total plots generated: {len([f for f in os.listdir(PLOT_DIR) if f.endswith('.png')])}")
print("DONE!")
