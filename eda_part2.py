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
