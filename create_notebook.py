"""
Convert eda_full.py into a well-structured Jupyter Notebook (.ipynb) for Google Colab.
"""
import json

def make_cell(cell_type, source, metadata=None):
    cell = {
        "cell_type": cell_type,
        "metadata": metadata or {},
        "source": source if isinstance(source, list) else [source]
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell

cells = []

# Title markdown
cells.append(make_cell("markdown", [
    "# NFPC Phase 1 -- Exploratory Data Analysis Report\n",
    "**National Fraud Prevention Challenge (NFPC)**\n",
    "Reserve Bank Innovation Hub (RBIH) x IIT Delhi TRYST\n",
    "\n",
    "---\n",
    "\n",
    "**Objective:** Analyze synthetic banking data to identify mule account patterns,\n",
    "design predictive features, and propose a modeling strategy for Phase 2.\n",
    "\n",
    "**Dataset:** ~40K customers, ~40K accounts, ~7.4M transactions, 24K labeled accounts (~1.1% mule rate)"
]))

# Setup cell
cells.append(make_cell("markdown", ["## Setup & Configuration"]))
cells.append(make_cell("code", [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from scipy import stats\n",
    "import warnings, os\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)\n",
    "plt.rcParams.update({'figure.dpi': 120, 'figure.figsize': (12, 6)})\n",
    "\n",
    "# Update this path for your environment\n",
    "DATA_DIR = '/content/drive/MyDrive/NFPC/EDA-Phase-1'  # Google Colab path\n",
    "# DATA_DIR = r'C:\\Users\\jaivi\\OneDrive\\Desktop\\upi\\IITD-Tryst-Hackathon\\EDA-Phase-1'  # Local path"
]))

# Section 1: Data Loading
cells.append(make_cell("markdown", [
    "## 1. Data Loading & Schema Understanding\n",
    "Load all 7 CSV files and parse date columns."
]))
cells.append(make_cell("code", [
    "# Load all datasets\n",
    "customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))\n",
    "accounts = pd.read_csv(os.path.join(DATA_DIR, 'accounts.csv'))\n",
    "linkage = pd.read_csv(os.path.join(DATA_DIR, 'customer_account_linkage.csv'))\n",
    "products = pd.read_csv(os.path.join(DATA_DIR, 'product_details.csv'))\n",
    "labels = pd.read_csv(os.path.join(DATA_DIR, 'train_labels.csv'))\n",
    "test = pd.read_csv(os.path.join(DATA_DIR, 'test_accounts.csv'))\n",
    "\n",
    "# Load transactions (6 parts)\n",
    "txn_parts = [pd.read_csv(os.path.join(DATA_DIR, f'transactions_part_{i}.csv')) for i in range(6)]\n",
    "transactions = pd.concat(txn_parts, ignore_index=True)\n",
    "del txn_parts\n",
    "\n",
    "# Parse dates\n",
    "for col in ['date_of_birth', 'relationship_start_date']:\n",
    "    customers[col] = pd.to_datetime(customers[col], errors='coerce')\n",
    "for col in ['account_opening_date', 'last_mobile_update_date', 'last_kyc_date', 'freeze_date', 'unfreeze_date']:\n",
    "    accounts[col] = pd.to_datetime(accounts[col], errors='coerce')\n",
    "transactions['transaction_timestamp'] = pd.to_datetime(transactions['transaction_timestamp'], errors='coerce')\n",
    "labels['mule_flag_date'] = pd.to_datetime(labels['mule_flag_date'], errors='coerce')\n",
    "\n",
    "# Display shapes\n",
    "for name, df in {'customers': customers, 'accounts': accounts, 'transactions': transactions,\n",
    "                  'linkage': linkage, 'products': products, 'labels': labels, 'test': test}.items():\n",
    "    print(f'{name}: {df.shape}')"
]))

cells.append(make_cell("code", [
    "# Missing values summary\n",
    "for name, df in {'customers': customers, 'accounts': accounts, 'transactions': transactions,\n",
    "                  'products': products, 'labels': labels}.items():\n",
    "    nulls = df.isnull().sum()\n",
    "    nulls = nulls[nulls > 0]\n",
    "    if len(nulls) > 0:\n",
    "        print(f'\\n--- {name} ---')\n",
    "        for col, cnt in nulls.items():\n",
    "            print(f'  {col}: {cnt:,} ({cnt/len(df)*100:.1f}%)')"
]))

cells.append(make_cell("code", [
    "# Join tables for analysis\n",
    "train = labels.merge(accounts, on='account_id', how='left')\n",
    "train = train.merge(linkage, on='account_id', how='left')\n",
    "train = train.merge(customers, on='customer_id', how='left')\n",
    "train = train.merge(products, on='customer_id', how='left')\n",
    "\n",
    "mule = train[train['is_mule'] == 1]\n",
    "legit = train[train['is_mule'] == 0]\n",
    "print(f'Train shape: {train.shape}')\n",
    "print(f'Mule: {len(mule)}, Legitimate: {len(legit)}')"
]))

# Section 2: Target Variable
cells.append(make_cell("markdown", [
    "## 2. Target Variable Deep Analysis\n",
    "Class distribution and alert reason breakdown."
]))
cells.append(make_cell("code", [
    "mule_rate = labels['is_mule'].mean()\n",
    "mule_count = labels['is_mule'].sum()\n",
    "legit_count = len(labels) - mule_count\n",
    "\n",
    "print(f'Class Distribution: {legit_count:,} legitimate ({(1-mule_rate)*100:.1f}%) vs {mule_count:,} mule ({mule_rate*100:.2f}%)')\n",
    "print(f'Imbalance ratio: {int(legit_count/mule_count)}:1')\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "labels['is_mule'].value_counts().plot.bar(ax=axes[0], color=['#2ecc71', '#e74c3c'])\n",
    "axes[0].set_title('Class Distribution')\n",
    "axes[0].set_xticklabels(['Legitimate (0)', 'Mule (1)'], rotation=0)\n",
    "for i, v in enumerate(labels['is_mule'].value_counts().values):\n",
    "    axes[0].text(i, v + 100, f'{v:,}', ha='center', fontweight='bold')\n",
    "\n",
    "alert_reasons = mule[mule['alert_reason'].notna()]['alert_reason'].value_counts()\n",
    "alert_reasons.head(15).plot.barh(ax=axes[1], color='#e74c3c')\n",
    "axes[1].set_title('Top Alert Reasons (Mule Accounts)')\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(make_cell("code", [
    "# Temporal distribution of mule flagging\n",
    "mule_dates = mule[mule['mule_flag_date'].notna()]['mule_flag_date']\n",
    "fig, ax = plt.subplots(figsize=(14, 5))\n",
    "mule_dates.dt.to_period('M').value_counts().sort_index().plot(ax=ax, kind='bar', color='#e74c3c', alpha=0.8)\n",
    "ax.set_title('Monthly Distribution of Mule Flagging')\n",
    "plt.xticks(rotation=45)\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "branch_flags = mule[mule['flagged_by_branch'].notna()]['flagged_by_branch'].value_counts()\n",
    "print(f'Branches that flagged mules: {len(branch_flags)}')\n",
    "print(f'Top 5 branches account for: {branch_flags.head(5).sum()/mule_count*100:.1f}% of all flags')"
]))

# Section 3: Account-Level
cells.append(make_cell("markdown", ["## 3. Account-Level EDA (Mule vs Legitimate)"]))
cells.append(make_cell("code", [
    "# Balance distributions\n",
    "balance_cols = ['avg_balance', 'monthly_avg_balance', 'quarterly_avg_balance', 'daily_avg_balance']\n",
    "fig, axes = plt.subplots(2, 2, figsize=(16, 12))\n",
    "for idx, col in enumerate(balance_cols):\n",
    "    ax = axes[idx // 2][idx % 2]\n",
    "    for label, grp, color in [(0, legit, '#2ecc71'), (1, mule, '#e74c3c')]:\n",
    "        data = grp[col].dropna().clip(-50000, 500000)\n",
    "        ax.hist(data, bins=80, alpha=0.5, color=color, label=f'{\"Mule\" if label else \"Legit\"}', density=True)\n",
    "    ax.set_title(f'{col} Distribution')\n",
    "    ax.legend()\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "for col in balance_cols:\n",
    "    print(f'{col}: Legit median={legit[col].median():,.0f} | Mule median={mule[col].median():,.0f}')"
]))

cells.append(make_cell("code", [
    "# Account status\n",
    "print('Account Status:')\n",
    "for status in train['account_status'].unique():\n",
    "    lc = (legit['account_status'] == status).sum()\n",
    "    mc = (mule['account_status'] == status).sum()\n",
    "    print(f'  {status}: Legit {lc:,} ({lc/len(legit)*100:.1f}%) | Mule {mc:,} ({mc/len(mule)*100:.1f}%)')\n",
    "\n",
    "# Account age\n",
    "ref_date = pd.Timestamp('2025-06-30')\n",
    "train['account_age_days'] = (ref_date - train['account_opening_date']).dt.days\n",
    "mule = train[train['is_mule'] == 1]\n",
    "legit = train[train['is_mule'] == 0]\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(14, 5))\n",
    "ax.hist(legit['account_age_days'].dropna(), bins=60, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)\n",
    "ax.hist(mule['account_age_days'].dropna(), bins=60, alpha=0.5, color='#e74c3c', label='Mule', density=True)\n",
    "ax.set_title('Account Age Distribution')\n",
    "ax.legend()\n",
    "plt.show()\n",
    "\n",
    "print(f'Legit median age: {legit[\"account_age_days\"].median():,.0f} days')\n",
    "print(f'Mule median age: {mule[\"account_age_days\"].median():,.0f} days')\n",
    "\n",
    "# Freeze pattern\n",
    "print(f'\\nAccounts ever frozen: Legit {legit[\"freeze_date\"].notna().mean()*100:.1f}% | Mule {mule[\"freeze_date\"].notna().mean()*100:.1f}%')"
]))

# Section 4: Customer-Level
cells.append(make_cell("markdown", ["## 4. Customer-Level EDA"]))
cells.append(make_cell("code", [
    "train['customer_age'] = (ref_date - train['date_of_birth']).dt.days / 365.25\n",
    "train['relationship_years'] = (ref_date - train['relationship_start_date']).dt.days / 365.25\n",
    "mule = train[train['is_mule'] == 1]\n",
    "legit = train[train['is_mule'] == 0]\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(16, 5))\n",
    "axes[0].hist(legit['customer_age'].dropna(), bins=50, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)\n",
    "axes[0].hist(mule['customer_age'].dropna(), bins=50, alpha=0.5, color='#e74c3c', label='Mule', density=True)\n",
    "axes[0].set_title('Customer Age'); axes[0].legend()\n",
    "axes[1].hist(legit['relationship_years'].dropna(), bins=50, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)\n",
    "axes[1].hist(mule['relationship_years'].dropna(), bins=50, alpha=0.5, color='#e74c3c', label='Mule', density=True)\n",
    "axes[1].set_title('Relationship Tenure'); axes[1].legend()\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "# Digital banking adoption\n",
    "digital_cols = ['mobile_banking_flag', 'internet_banking_flag', 'atm_card_flag', 'demat_flag', 'credit_card_flag', 'fastag_flag']\n",
    "fig, ax = plt.subplots(figsize=(12, 5))\n",
    "x = np.arange(len(digital_cols))\n",
    "ax.bar(x - 0.2, [(legit[c] == 'Y').mean()*100 for c in digital_cols], 0.4, label='Legitimate', color='#2ecc71')\n",
    "ax.bar(x + 0.2, [(mule[c] == 'Y').mean()*100 for c in digital_cols], 0.4, label='Mule', color='#e74c3c')\n",
    "ax.set_xticks(x)\n",
    "ax.set_xticklabels([c.replace('_flag', '') for c in digital_cols], rotation=30)\n",
    "ax.set_title('Digital Banking Adoption'); ax.legend()\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# Section 5: Transaction-Level
cells.append(make_cell("markdown", ["## 5. Transaction-Level EDA"]))
cells.append(make_cell("code", [
    "# Merge transactions with labels\n",
    "txn_labeled = transactions.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')\n",
    "txn_mule = txn_labeled[txn_labeled['is_mule'] == 1]\n",
    "txn_legit = txn_labeled[txn_labeled['is_mule'] == 0]\n",
    "\n",
    "# Per-account transaction stats\n",
    "acct_txn_stats = transactions.groupby('account_id').agg(\n",
    "    txn_count=('transaction_id', 'count'),\n",
    "    total_volume=('amount', lambda x: x.abs().sum()),\n",
    "    avg_amount=('amount', lambda x: x.abs().mean()),\n",
    "    unique_channels=('channel', 'nunique'),\n",
    "    unique_counterparties=('counterparty_id', 'nunique'),\n",
    "    credit_count=('txn_type', lambda x: (x == 'C').sum()),\n",
    "    debit_count=('txn_type', lambda x: (x == 'D').sum()),\n",
    ").reset_index()\n",
    "acct_txn_stats = acct_txn_stats.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')\n",
    "acct_mule = acct_txn_stats[acct_txn_stats['is_mule'] == 1]\n",
    "acct_legit = acct_txn_stats[acct_txn_stats['is_mule'] == 0]\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(16, 5))\n",
    "axes[0].hist(acct_legit['txn_count'].clip(0, 1000), bins=60, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)\n",
    "axes[0].hist(acct_mule['txn_count'].clip(0, 1000), bins=60, alpha=0.5, color='#e74c3c', label='Mule', density=True)\n",
    "axes[0].set_title('Transactions per Account'); axes[0].legend()\n",
    "axes[1].hist(np.log1p(acct_legit['total_volume']), bins=60, alpha=0.5, color='#2ecc71', label='Legitimate', density=True)\n",
    "axes[1].hist(np.log1p(acct_mule['total_volume']), bins=60, alpha=0.5, color='#e74c3c', label='Mule', density=True)\n",
    "axes[1].set_title('Total Volume (log scale)'); axes[1].legend()\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "print('Metric comparisons (Mule vs Legit):')\n",
    "for col in ['txn_count', 'total_volume', 'avg_amount', 'unique_counterparties']:\n",
    "    lv, mv = acct_legit[col].median(), acct_mule[col].median()\n",
    "    print(f'  {col}: Legit {lv:,.1f} | Mule {mv:,.1f} | Ratio {mv/lv:.2f}x')"
]))

cells.append(make_cell("code", [
    "# Temporal patterns\n",
    "txn_labeled['hour'] = txn_labeled['transaction_timestamp'].dt.hour\n",
    "txn_labeled['dow'] = txn_labeled['transaction_timestamp'].dt.dayofweek\n",
    "\n",
    "fig, axes = plt.subplots(1, 3, figsize=(20, 5))\n",
    "for cls, color, label in [(0, '#2ecc71', 'Legitimate'), (1, '#e74c3c', 'Mule')]:\n",
    "    grp = txn_labeled[txn_labeled['is_mule'] == cls]\n",
    "    grp['hour'].value_counts().sort_index().plot(ax=axes[0], color=color, label=label, alpha=0.7)\n",
    "    grp['dow'].value_counts().sort_index().plot(ax=axes[1], color=color, label=label, alpha=0.7)\n",
    "    grp['transaction_timestamp'].dt.month.value_counts().sort_index().plot(ax=axes[2], color=color, label=label, alpha=0.7)\n",
    "axes[0].set_title('Hour of Day'); axes[0].legend()\n",
    "axes[1].set_title('Day of Week')\n",
    "axes[2].set_title('Month of Year')\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# Section 6: Mule Patterns
cells.append(make_cell("markdown", [
    "## 6. Known Mule Pattern Detection\n",
    "Investigating all 12 known mule behavior patterns from the dataset documentation."
]))
cells.append(make_cell("code", [
    "# Pattern 1: Dormant Activation\n",
    "print('=== 6.1 Dormant Activation ===')\n",
    "txn_sorted = txn_labeled[['account_id', 'transaction_timestamp', 'is_mule']].sort_values(['account_id', 'transaction_timestamp'])\n",
    "txn_sorted['gap_days'] = txn_sorted.groupby('account_id')['transaction_timestamp'].diff().dt.days\n",
    "max_gaps = txn_sorted.groupby('account_id')['gap_days'].max().reset_index()\n",
    "max_gaps = max_gaps.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')\n",
    "print(f'Median max gap: Legit {max_gaps[max_gaps[\"is_mule\"]==0][\"gap_days\"].median():.0f} days | Mule {max_gaps[max_gaps[\"is_mule\"]==1][\"gap_days\"].median():.0f} days')\n",
    "\n",
    "# Pattern 2: Structuring\n",
    "print('\\n=== 6.2 Structuring ===')\n",
    "near_thresh = txn_labeled[(txn_labeled['amount'].abs() >= 45000) & (txn_labeled['amount'].abs() < 50000)]\n",
    "total_by_class = txn_labeled.groupby('is_mule')['transaction_id'].count()\n",
    "near_by_class = near_thresh.groupby('is_mule')['transaction_id'].count()\n",
    "print(f'Near-threshold rate: Legit {near_by_class.get(0,0)/total_by_class.get(0,1)*100:.3f}% | Mule {near_by_class.get(1,0)/total_by_class.get(1,1)*100:.3f}%')\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(14, 5))\n",
    "bins = np.arange(0, 100001, 1000)\n",
    "ax.hist(txn_legit['amount'].abs().clip(0, 100000), bins=bins, alpha=0.4, color='#2ecc71', label='Legitimate', density=True)\n",
    "ax.hist(txn_mule['amount'].abs().clip(0, 100000), bins=bins, alpha=0.4, color='#e74c3c', label='Mule', density=True)\n",
    "ax.axvline(x=50000, color='black', linestyle='--', label='50K Threshold')\n",
    "ax.set_title('Amount Distribution Near Reporting Threshold'); ax.legend()\n",
    "plt.show()"
]))

cells.append(make_cell("code", [
    "# Pattern 4: Fan-In / Fan-Out\n",
    "print('=== 6.4 Fan-In / Fan-Out ===')\n",
    "fan_stats = txn_labeled.groupby(['account_id', 'is_mule']).agg(\n",
    "    credit_sources=('counterparty_id', lambda x: x[txn_labeled.loc[x.index, 'txn_type'] == 'C'].nunique() if len(x) > 0 else 0),\n",
    "    debit_dests=('counterparty_id', lambda x: x[txn_labeled.loc[x.index, 'txn_type'] == 'D'].nunique() if len(x) > 0 else 0),\n",
    ").reset_index()\n",
    "print(f'Credit sources: Legit {fan_stats[fan_stats[\"is_mule\"]==0][\"credit_sources\"].median():.0f} | Mule {fan_stats[fan_stats[\"is_mule\"]==1][\"credit_sources\"].median():.0f}')\n",
    "print(f'Debit dests: Legit {fan_stats[fan_stats[\"is_mule\"]==0][\"debit_dests\"].median():.0f} | Mule {fan_stats[fan_stats[\"is_mule\"]==1][\"debit_dests\"].median():.0f}')\n",
    "\n",
    "# Pattern 5: Geographic Anomaly\n",
    "print('\\n=== 6.5 Geographic Anomaly ===')\n",
    "train['pin_mismatch'] = (train['customer_pin'] != train['branch_pin']).astype(int)\n",
    "print(f'PIN mismatch: Legit {train[train[\"is_mule\"]==0][\"pin_mismatch\"].mean()*100:.1f}% | Mule {train[train[\"is_mule\"]==1][\"pin_mismatch\"].mean()*100:.1f}%')\n",
    "\n",
    "# Pattern 7: Income Mismatch\n",
    "print('\\n=== 6.7 Income Mismatch ===')\n",
    "mismatch = acct_txn_stats.merge(accounts[['account_id', 'avg_balance']], on='account_id', how='left')\n",
    "mismatch['volume_balance_ratio'] = mismatch['total_volume'] / (mismatch['avg_balance'].abs() + 1)\n",
    "print(f'Volume/Balance ratio: Legit {mismatch[mismatch[\"is_mule\"]==0][\"volume_balance_ratio\"].median():,.1f} | Mule {mismatch[mismatch[\"is_mule\"]==1][\"volume_balance_ratio\"].median():,.1f}')"
]))

cells.append(make_cell("code", [
    "# Pattern 12: Branch-Level Collusion\n",
    "print('=== 6.12 Branch-Level Collusion ===')\n",
    "branch_mule_rate = train.groupby('branch_code').agg(\n",
    "    total=('is_mule', 'count'), mules=('is_mule', 'sum')\n",
    ").reset_index()\n",
    "branch_mule_rate['mule_rate'] = branch_mule_rate['mules'] / branch_mule_rate['total'] * 100\n",
    "print(f'Total branches: {len(branch_mule_rate)}')\n",
    "print(f'Highest mule rate: {branch_mule_rate[\"mule_rate\"].max():.1f}%')\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(14, 5))\n",
    "ax.hist(branch_mule_rate['mule_rate'], bins=50, color='#9b59b6', alpha=0.7)\n",
    "ax.axvline(x=branch_mule_rate['mule_rate'].quantile(0.95), color='red', linestyle='--', label='95th percentile')\n",
    "ax.set_title('Branch Mule Rate Distribution'); ax.legend()\n",
    "plt.show()"
]))

# Section 7: Network Analysis
cells.append(make_cell("markdown", ["## 7. Network / Relationship Analysis"]))
cells.append(make_cell("code", [
    "# Counterparty network\n",
    "network_stats = transactions.groupby('account_id').agg(\n",
    "    in_degree=('counterparty_id', lambda x: x[transactions.loc[x.index, 'txn_type'] == 'C'].nunique()),\n",
    "    out_degree=('counterparty_id', lambda x: x[transactions.loc[x.index, 'txn_type'] == 'D'].nunique()),\n",
    "    total_degree=('counterparty_id', 'nunique')\n",
    ").reset_index()\n",
    "network_stats = network_stats.merge(labels[['account_id', 'is_mule']], on='account_id', how='inner')\n",
    "\n",
    "for col in ['in_degree', 'out_degree', 'total_degree']:\n",
    "    print(f'{col}: Legit {network_stats[network_stats[\"is_mule\"]==0][col].median():.0f} | Mule {network_stats[network_stats[\"is_mule\"]==1][col].median():.0f}')\n",
    "\n",
    "# Shared counterparties\n",
    "mule_accts_list = labels[labels['is_mule'] == 1]['account_id'].tolist()\n",
    "mule_txns = transactions[transactions['account_id'].isin(mule_accts_list)]\n",
    "mule_cps = mule_txns.groupby('counterparty_id')['account_id'].nunique()\n",
    "shared = mule_cps[mule_cps > 1]\n",
    "print(f'\\nCounterparties shared by 2+ mules: {len(shared):,}')\n",
    "print(f'Max mules sharing one counterparty: {shared.max() if len(shared) > 0 else 0}')"
]))

# Section 8-10: Summary
cells.append(make_cell("markdown", [
    "## 8. Data Quality & Leakage Analysis\n",
    "\n",
    "**Critical Leakage Warnings:**\n",
    "- `mule_flag_date`, `alert_reason`, `flagged_by_branch` -- HIGH risk, only populated for flagged mules\n",
    "- `account_status` (frozen), `freeze_date` -- MEDIUM risk, may be a consequence of detection\n",
    "\n",
    "**Label Noise:** The README states labels may contain noise. Models must be robust."
]))

cells.append(make_cell("markdown", [
    "## 9. Feature Engineering Plan (46 Features)\n",
    "\n",
    "| Category | Count | Examples |\n",
    "|---|---|---|\n",
    "| A. Behavioral | 15 | txn_count, total_volume, credit_debit_ratio, counterparty_entropy |\n",
    "| B. Temporal | 10 | night_txn_ratio, burst_score, dormancy_days_before_burst |\n",
    "| C. Graph/Network | 8 | in_degree, out_degree, shared_counterparties_with_mules |\n",
    "| D. Profile | 8 | account_age_days, kyc_document_count, pin_mismatch |\n",
    "| E. Anomaly/Composite | 5 | pass_through_score, structuring_score, layered_composite |\n",
    "\n",
    "See the full PDF report for detailed feature specifications."
]))

cells.append(make_cell("markdown", [
    "## 10. Modelling Strategy\n",
    "\n",
    "| Component | Method | Rationale |\n",
    "|---|---|---|\n",
    "| Base classifier | LightGBM + scale_pos_weight | Efficient, handles imbalance |\n",
    "| Graph features | Node2Vec / GNN | Captures network structure |\n",
    "| Anomaly detection | Isolation Forest | Unsupervised novel patterns |\n",
    "| Ensemble | Weighted average | Combines paradigm strengths |\n",
    "| Imbalance | SMOTE + Tomek + focal loss | Multi-pronged |\n",
    "| Validation | Stratified temporal K-Fold | Prevents leakage |\n",
    "\n",
    "---\n",
    "*End of EDA Notebook | National Fraud Prevention Challenge Phase 1*"
]))

# Build notebook
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        },
        "colab": {
            "provenance": [],
            "toc_visible": True
        }
    },
    "cells": cells
}

out_path = r'C:\Users\jaivi\OneDrive\Desktop\upi\NFPC_EDA_Notebook.ipynb'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)
print(f"Notebook saved to: {out_path}")
print(f"Total cells: {len(cells)}")
