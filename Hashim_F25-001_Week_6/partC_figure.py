"""One board figure: sorted household-normalized comparison."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import vizlib
ROOT=Path(__file__).resolve().parent

def main():
    d=pd.read_csv(ROOT/'clean/district_grid.csv').sort_values('interruptions_per_1000_households')
    pooled=1000*d.outages.sum()/d.households.sum();vizlib.style_defaults()
    fig,ax=plt.subplots(figsize=(10,8))
    ax.barh(d.code+'  '+d.district,d.interruptions_per_1000_households,color='#0072B2',height=.7)
    ax.axvline(pooled,color='#16202E',ls='--',lw=1.3,label=f'Pooled national rate: {pooled:.1f}')
    for y,(_,r) in enumerate(d.iterrows()):
        ax.text(r.interruptions_per_1000_households+.35,y,f'{r.interruptions_per_1000_households:.1f}',va='center',fontsize=8)
    ax.set_xlim(0,59);ax.set_xlabel('Recorded feeder interruptions per 1,000 billed domestic connections (households)')
    ax.set_title('Prioritize D12, D11 and D13 for reliability review',fontsize=15,pad=36)
    ax.text(0,1.025,'Reader: National Grid Authority budget board • D13 combines high burden with high rate',transform=ax.transAxes,fontsize=10)
    ax.grid(axis='y',visible=False);ax.legend(loc='lower right');fig.tight_layout()
    vizlib.save_fig(fig,ROOT/'partC_figure.png','Source: synthetic CDB601220 Week 6 district register; cleaned by partA_process.py. All 24 districts; same 12-month register window.\nRate = interruptions ÷ billed domestic connections × 1,000. Descending rank from top; linear zero baseline; no suppression or imputation of interruptions.\nFeeder-event rate is a comparative proxy, not household interruption frequency (SAIFI); denominator is all billed domestic connections.')
    plt.close(fig)
    note=f"""# Task C — note to the budget board

Reader: National Grid Authority reliability-budget board. Message: prioritize D12 (Lashkar), D11 (Kotla), and D13 (Mehrabad) for reliability review because their feeder interruptions per 1,000 billed domestic connections are highest.

The figure divides the same twelve-month interruption count by billed domestic connections (households) and multiplies by 1,000. This compares recorded feeder-event burden relative to service size; it does not estimate interruptions experienced by each customer or SAIFI, because affected-customer counts are unavailable. The pooled benchmark is {pooled:.1f}, computed from sums, not an average of district rates. No further electrification adjustment is applied: the denominator already describes billed connections, and three electrification percentages are missing.

A horizontal bar chart gives every district equal visual space; the five largest populations contain 59.9% of people in only 12.6% of land. Rates are ordered descending, drawn on a linear zero baseline and labelled numerically. The single blue hue has no categorical meaning, while the national benchmark uses a labelled dashed line. There are no bins, class breaks, map projection, nonlinear scaling, smoothing, or exclusions. All 24 districts remain. The source supplies a common twelve-month period but no precise district-period dates, so those dates are not invented. No district is suppressed: this is an illustrative descriptive ranking, not an inferential claim about precise causal risk.

Counterfactual: raw counts would select D17 (Qilabad), D13 (Mehrabad), and D24 (Zhobara). Only D13 appears in both lists. Count-led allocation would direct attention away from D12 and D11 toward larger D17 and D24. Count correlates with household size at +0.991; rate correlates at only +0.175. D13 has both a large connection base and a high relative interruption burden; its income is also jointly lowest at $2,600 per person/year (shared with D22). This makes its overlap an equity concern, although income association does not prove causation. A final budget should consider engineering costs and affected customers alongside this screening figure.
"""
    (ROOT/'partC_note.md').write_text(note)
    print('Task C: board figure and note written.')
if __name__=='__main__':main()
