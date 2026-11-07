"""Three question types: trend, composition, relationship."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import vizlib
ROOT=Path(__file__).resolve().parent
SOURCE='Source: synthetic CDB601220 Week 6 data; processed by partA_process.py.'
BLUE='#0072B2';ORANGE='#D55E00'

def main():
    vizlib.style_defaults()
    with (ROOT/'colour_audit.txt').open('w') as f:
        import contextlib
        with contextlib.redirect_stdout(f):
            for kind in ['deutan','protan','tritan']: vizlib.cvd_report([BLUE,ORANGE],kind)
            for kind in [None,'deutan','protan','tritan']:
                print('Worst pair',kind,vizlib.worst_pair([BLUE,ORANGE],kind))
        f.write('Identity also encoded with explicit labels, markers, or hatching.\n')
    g=pd.read_csv(ROOT/'clean/grid_daily.csv',parse_dates=['date'])
    s=g[g.zone=='P1'].set_index('date').peak_load_mw.reindex(pd.date_range('2025-04-01','2026-08-31'))
    smooth=s.rolling(7,min_periods=7).mean()
    fig,ax=plt.subplots(figsize=(10,4.4));ax.plot(s.index,s,color=BLUE,alpha=.22,lw=.8,label='Reported daily maximum')
    ax.plot(smooth.index,smooth,color=BLUE,label='Trailing 7-day mean (7 valid days required)')
    ax.set(title='P1 peak demand rises in summer in both observed years',ylabel='Daily peak load (MW)',xlabel='Calendar date');ax.set_ylim(bottom=0);ax.legend(loc='upper left',fontsize=8)
    fig.tight_layout();vizlib.save_fig(fig,ROOT/'partB_1.png',SOURCE+'\nP1 only; 2025-04-01–2026-08-31. Daily maxima; trailing 7 calendar days; no imputation. September excluded as partial.\nGaps and failed readings remain missing; smoothing stops across them. Decision: schedule capacity and maintenance outside peak season.');plt.close(fig)
    m=pd.read_csv(ROOT/'clean/generation_mix.csv',parse_dates=['month']); t=pd.read_csv(ROOT/'clean/generation_totals.csv',parse_dates=['month']).set_index('month').mwh
    ends=[m.month.min(),m.month.max()]; solar=m[m.subsource=='Solar'].set_index('month').mwh
    growth=100*(solar.iloc[-1]/solar.iloc[0]-1);fall=100*(t.iloc[-1]/t.iloc[0]-1)
    assert round(growth,1)==82.1 and round(fall,1)==-5.0
    fig,ax=plt.subplots(figsize=(10,4.7));x=np.arange(2); ss=solar.loc[ends]/1e6; rest=(t.loc[ends]-solar.loc[ends])/1e6
    ax.bar(x,ss,width=.5,color=ORANGE,label='Solar',hatch='///');ax.bar(x,rest,bottom=ss,width=.5,color=BLUE,label='All other leaf categories (7 combined)')
    for i,month in enumerate(ends):
        ax.text(i,t.loc[month]/1e6+.15,f'Total {t.loc[month]/1e6:.2f}m MWh',ha='center')
        ax.text(i,ss.loc[month]/2,f'{solar.loc[month]:,.0f} MWh | {100*solar.loc[month]/t.loc[month]:.1f}%',ha='center',fontsize=9,color='black',bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
    ax.set_xticks(x,[x.strftime('%b %Y') for x in ends]);ax.set_ylim(0,13);ax.set_ylabel('Generation (million MWh)');ax.set_title(f'Solar output grows {growth:.1f}% while total generation falls {abs(fall):.1f}%');ax.legend(loc='upper right',fontsize=8)
    fig.tight_layout();vizlib.save_fig(fig,ROOT/'partB_2.png',SOURCE+'\nComposition: published complete months April 2025 and September 2026; monthly MWh sums of disjoint leaves; total rows excluded from stacks.\nSolar explicit; all other seven leaves combined. No smoothing. Decision: describe real solar growth alongside the shrinking denominator.');plt.close(fig)
    d=pd.read_csv(ROOT/'clean/district_grid.csv');fig,ax=plt.subplots(figsize=(10,4.8))
    ax.scatter(d.households/1000,d.outages/1000,s=40,color=BLUE)
    for _,r in d[d.code.isin(['D17','D13','D24','D12','D11'])].iterrows(): ax.annotate(r.code,(r.households/1000,r.outages/1000),xytext=(5,5),textcoords='offset points')
    ax.set(xlim=(0,1800),ylim=(0,72),xlabel='Billed domestic connections (thousand households)',ylabel='Recorded feeder interruptions (thousands)',title=f'Interruption counts track district size (r = {d.households.corr(d.outages):.3f})')
    fig.tight_layout();vizlib.save_fig(fig,ROOT/'partB_3.png',SOURCE+'\nRelationship: all 24 districts; same 12-month register period (exact dates unspecified); Pearson r; no fit, exclusions or transformations except /1000.\nLabels: top three by count or rate. Decision: normalize district comparisons before allocating reliability funds.');plt.close(fig)
    print('Task B: three 300 dpi figures and colour audit written.')
if __name__=='__main__':main()
