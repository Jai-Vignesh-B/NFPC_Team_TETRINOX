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
