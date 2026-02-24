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
