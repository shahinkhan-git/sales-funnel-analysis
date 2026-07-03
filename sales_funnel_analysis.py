"""
Sales Funnel Analysis
=====================
Author  : Shahin Khan
Purpose : Analyse B2B sales pipeline data to identify conversion rates,
          revenue by source, rep performance, and monthly trends.

Dependencies: pandas, matplotlib, seaborn, numpy
Run with    : python sales_funnel_analysis.py
Outputs     : 4 chart PNG files saved to the same directory
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── Style ─────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':        'DejaVu Sans',
    'axes.facecolor':     '#1e1e1e',
    'figure.facecolor':   '#161616',
    'axes.edgecolor':     '#333333',
    'axes.labelcolor':    '#bfbfbf',
    'xtick.color':        '#bfbfbf',
    'ytick.color':        '#bfbfbf',
    'grid.color':         '#2a2a2a',
    'grid.linewidth':     0.8,
    'text.color':         '#ffffff',
    'axes.titlecolor':    '#ffffff',
    'axes.titlesize':     13,
    'axes.labelsize':     11,
})

GOLD    = '#ffb400'
TEAL    = '#00c9a7'
CORAL   = '#ff6f61'
PURPLE  = '#7c5cfc'
BLUE    = '#38bdf8'
MUTED   = '#a6a6a6'
CARD_BG = '#1e1e1e'

# ── Load data ─────────────────────────────────────────────────────────────
df = pd.read_csv('sales_funnel_data.csv')
print(f"Loaded {len(df)} deals from pipeline\n")

# ── Stage order ───────────────────────────────────────────────────────────
STAGE_ORDER = ['Discovery', 'Qualified', 'Proposal', 'Closed Won', 'Closed Lost']
df['stage'] = pd.Categorical(df['stage'], categories=STAGE_ORDER, ordered=True)

# ── Summary stats ─────────────────────────────────────────────────────────
total_deals    = len(df)
won_deals      = len(df[df['stage'] == 'Closed Won'])
lost_deals     = len(df[df['stage'] == 'Closed Lost'])
win_rate       = won_deals / (won_deals + lost_deals) * 100
total_revenue  = df[df['stage'] == 'Closed Won']['deal_value'].sum()
avg_deal_size  = df[df['stage'] == 'Closed Won']['deal_value'].mean()
avg_days       = df[df['stage'] == 'Closed Won']['days_in_stage'].mean()

print("=" * 50)
print("SALES FUNNEL SUMMARY")
print("=" * 50)
print(f"Total Deals in Pipeline : {total_deals}")
print(f"Closed Won              : {won_deals}")
print(f"Closed Lost             : {lost_deals}")
print(f"Win Rate                : {win_rate:.1f}%")
print(f"Total Revenue (Won)     : ${total_revenue:,.0f}")
print(f"Average Deal Size       : ${avg_deal_size:,.0f}")
print(f"Avg Days to Close       : {avg_days:.1f} days")
print("=" * 50)

# ══════════════════════════════════════════════════════════════════════════
# CHART 1 — Sales Funnel (Funnel Chart)
# ══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor('#161616')
ax.set_facecolor('#161616')

funnel_stages  = ['Discovery', 'Qualified', 'Proposal', 'Closed Won']
funnel_colours = [BLUE, TEAL, GOLD, '#22c55e']
counts = [len(df[df['stage'] == s]) for s in funnel_stages]
max_w  = max(counts)

for i, (stage, count, colour) in enumerate(zip(funnel_stages, counts, funnel_colours)):
    bar_w  = count / max_w
    x_left = (1 - bar_w) / 2
    rect   = mpatches.FancyBboxPatch(
        (x_left, i * 1.4), bar_w, 1.0,
        boxstyle="round,pad=0.02",
        linewidth=0,
        facecolor=colour,
        alpha=0.85
    )
    ax.add_patch(rect)
    ax.text(0.5, i * 1.4 + 0.5, f'{stage}  —  {count} deals',
            ha='center', va='center',
            fontsize=12, fontweight='600', color='#000000')
    if i > 0:
        prev = counts[i - 1]
        conv = count / prev * 100
        ax.text(x_left - 0.03, i * 1.4 + 0.5,
                f'{conv:.0f}%', ha='right', va='center',
                fontsize=10, color=MUTED)

ax.set_xlim(0, 1)
ax.set_ylim(-0.3, len(funnel_stages) * 1.4 + 0.2)
ax.axis('off')
ax.set_title('Sales Funnel — Stage Conversion', pad=20, fontsize=14, fontweight='700', color='white')

# KPI strip at bottom
kpis = [
    ('Win Rate', f'{win_rate:.0f}%'),
    ('Total Revenue', f'${total_revenue/1e6:.2f}M'),
    ('Avg Deal', f'${avg_deal_size/1e3:.0f}K'),
    ('Avg Close', f'{avg_days:.0f} days'),
]
for j, (label, val) in enumerate(kpis):
    x = 0.125 + j * 0.25
    ax.text(x, -0.15, val, ha='center', fontsize=13, fontweight='700', color=GOLD, transform=ax.transAxes)
    ax.text(x, -0.22, label, ha='center', fontsize=9, color=MUTED, transform=ax.transAxes)

plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig('chart_1_funnel.png', dpi=150, bbox_inches='tight', facecolor='#161616')
plt.close()
print("✓ chart_1_funnel.png saved")

# ══════════════════════════════════════════════════════════════════════════
# CHART 2 — Revenue by Lead Source (Horizontal Bar)
# ══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#161616')
ax.set_facecolor(CARD_BG)

won = df[df['stage'] == 'Closed Won']
source_rev = won.groupby('lead_source')['deal_value'].sum().sort_values()
colours    = [GOLD, TEAL, CORAL, PURPLE][:len(source_rev)]

bars = ax.barh(source_rev.index, source_rev.values, color=colours, height=0.55, edgecolor='none')

for bar, val in zip(bars, source_rev.values):
    ax.text(val + 5000, bar.get_y() + bar.get_height()/2,
            f'${val/1000:.0f}K', va='center', fontsize=11, fontweight='600', color='white')

ax.set_xlabel('Total Revenue (USD)', labelpad=10)
ax.set_title('Revenue by Lead Source', pad=15, fontsize=14, fontweight='700')
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1000:.0f}K'))
ax.grid(axis='x', alpha=0.3)
ax.spines[['top', 'right', 'left']].set_visible(False)

plt.tight_layout()
plt.savefig('chart_2_revenue_by_source.png', dpi=150, bbox_inches='tight', facecolor='#161616')
plt.close()
print("✓ chart_2_revenue_by_source.png saved")

# ══════════════════════════════════════════════════════════════════════════
# CHART 3 — Rep Performance (Win Rate + Revenue)
# ══════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
fig.patch.set_facecolor('#161616')

for ax in [ax1, ax2]:
    ax.set_facecolor(CARD_BG)
    ax.spines[['top', 'right']].set_visible(False)

closed = df[df['stage'].isin(['Closed Won', 'Closed Lost'])]
rep_stats = closed.groupby('rep_name').apply(
    lambda x: pd.Series({
        'win_rate': (x['stage'] == 'Closed Won').mean() * 100,
        'revenue':  x[x['stage'] == 'Closed Won']['deal_value'].sum(),
        'deals':    len(x)
    })
).reset_index()

rep_colours = [GOLD, TEAL, CORAL, PURPLE, BLUE]

# Win rate
bars1 = ax1.bar(rep_stats['rep_name'], rep_stats['win_rate'],
                color=rep_colours[:len(rep_stats)], width=0.5, edgecolor='none')
ax1.set_title('Win Rate by Rep', fontsize=13, fontweight='700', pad=12)
ax1.set_ylabel('Win Rate (%)')
ax1.set_ylim(0, 110)
ax1.grid(axis='y', alpha=0.3)
for bar, val in zip(bars1, rep_stats['win_rate']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
             f'{val:.0f}%', ha='center', fontsize=10, fontweight='600', color='white')
ax1.set_xticklabels([n.split()[0] for n in rep_stats['rep_name']], fontsize=10)

# Revenue
bars2 = ax2.bar(rep_stats['rep_name'], rep_stats['revenue']/1000,
                color=rep_colours[:len(rep_stats)], width=0.5, edgecolor='none')
ax2.set_title('Revenue Closed by Rep', fontsize=13, fontweight='700', pad=12)
ax2.set_ylabel('Revenue (USD $K)')
ax2.grid(axis='y', alpha=0.3)
for bar, val in zip(bars2, rep_stats['revenue']/1000):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'${val:.0f}K', ha='center', fontsize=10, fontweight='600', color='white')
ax2.set_xticklabels([n.split()[0] for n in rep_stats['rep_name']], fontsize=10)

fig.suptitle('Sales Rep Performance Dashboard', fontsize=15, fontweight='700', y=1.01)
plt.tight_layout()
plt.savefig('chart_3_rep_performance.png', dpi=150, bbox_inches='tight', facecolor='#161616')
plt.close()
print("✓ chart_3_rep_performance.png saved")

# ══════════════════════════════════════════════════════════════════════════
# CHART 4 — Monthly Revenue Trend
# ══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor('#161616')
ax.set_facecolor(CARD_BG)

month_order = ['January','February','March','April','May','June']
monthly = (won.groupby('month')['deal_value']
           .sum()
           .reindex(month_order)
           .fillna(0))

ax.fill_between(range(len(monthly)), monthly.values/1000, alpha=0.18, color=GOLD)
ax.plot(range(len(monthly)), monthly.values/1000,
        color=GOLD, linewidth=2.5, marker='o', markersize=8,
        markerfacecolor=GOLD, markeredgecolor='#161616', markeredgewidth=2)

for i, val in enumerate(monthly.values):
    ax.text(i, val/1000 + 8, f'${val/1000:.0f}K',
            ha='center', fontsize=10, fontweight='600', color='white')

ax.set_xticks(range(len(monthly)))
ax.set_xticklabels([m[:3] for m in month_order], fontsize=11)
ax.set_ylabel('Revenue (USD $K)', labelpad=10)
ax.set_title('Monthly Closed Revenue — H1 2026', pad=15, fontsize=14, fontweight='700')
ax.grid(axis='y', alpha=0.3)
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.set_ylim(0, monthly.max()/1000 * 1.25)

# MoM growth annotation
for i in range(1, len(monthly)):
    growth = (monthly.values[i] - monthly.values[i-1]) / monthly.values[i-1] * 100
    colour = '#22c55e' if growth >= 0 else CORAL
    ax.annotate(f'{growth:+.0f}%',
                xy=(i, monthly.values[i]/1000),
                xytext=(i - 0.3, monthly.values[i]/1000 - 30),
                fontsize=9, color=colour, fontweight='600')

plt.tight_layout()
plt.savefig('chart_4_monthly_trend.png', dpi=150, bbox_inches='tight', facecolor='#161616')
plt.close()
print("✓ chart_4_monthly_trend.png saved")

print("\n✓ All 4 charts generated successfully.")
print(f"\nKey Insight: Referral leads generate {won[won['lead_source']=='Referral']['deal_value'].sum()/total_revenue*100:.0f}% of total revenue")
print(f"Best performer: {rep_stats.loc[rep_stats['revenue'].idxmax(), 'rep_name']} with ${rep_stats['revenue'].max()/1000:.0f}K closed")
print(f"Strongest month: {monthly.idxmax()} at ${monthly.max()/1000:.0f}K")
